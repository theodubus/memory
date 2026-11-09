#!/usr/bin/env python3
"""Le banc des adaptateurs (B-0030) : chaque adaptateur maintenu, éprouvé
sur un projet jetable de son langage, avec ses vrais outils.

Pour chaque langage, le banc pose un petit module de calcul et ses tests,
installe les dépendances, installe le socle avec l'adaptateur, puis vérifie
ce que le jalon 6 a vérifié pour Python :

- `socle verify --fast` passe sur le projet sain ;
- un test sans assertion, un test désactivé sans raison, une valeur
  attendue changée et une fonction publique sans test sont refusés, chacun
  par le contrôle attendu ;
- un correctif qui livre son test de régression passe, rejoué sur le
  parent ; un correctif sans test est refusé ;
- le balayage de mutation tourne, son rapport se lit, et le verdict passe
  au plafond mesuré et casse en dessous.

Puis un projet en deux langages, Python et Kotlin (ADR-0051) : un
adaptateur par langage déduit du dépôt, `verify` sur les deux, chaque test
jugé par son adaptateur, un correctif Kotlin qu'un test Python ne prouve
pas, et la mutation des deux.

Il faut les outils du langage (node, go, java et maven, ruby et bundler,
php et composer avec un pilote de couverture, le SDK .NET 8) et l'accès aux
registres de paquets. Les projets vivent dans un dossier temporaire, effacé à la fin.

    python3 bench/adapters.py                     # les langages, puis le projet en deux
    python3 bench/adapters.py --langages python+kotlin   # Python et Kotlin ensemble
    python3 bench/adapters.py --langages go,php   # quelques-uns
    python3 bench/adapters.py --garder            # garder les projets
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
MOTEUR = RACINE / "engine"
sys.path.insert(0, str(MOTEUR))

from socle import mutation  # noqa: E402

FIN = "FIN DES TESTS"


@dataclass
class Langage:
    adaptateur: str
    fichiers: dict[str, str]
    preparer: list[str]
    code: str  # le module que le plafond de mutation nomme
    creux: tuple[str, str, str]  # (fichier, avant, après)
    desactive: tuple[str, str, str]
    attendu: tuple[str, str, str]
    fonction: tuple[str, str, str]
    bogue: tuple[str, str, str]
    regression: tuple[str, str]  # (chemin, contenu)
    env: dict[str, str] = field(default_factory=dict)


# --------------------------------------------------------------------------
# Les projets jetables
# --------------------------------------------------------------------------

JS_CODE = """export function double(x) {
  return 2 * x;
}

export function suivant(x) {
  if (x > 100) {
    return x;
  }
  return aide(x);
}

function aide(x) {
  return x + 1;
}
"""
JS_TEST = f"""import {{ describe, expect, test }} from "vitest";
import {{ double, suivant }} from "../src/calc.js";

describe("calc", () => {{
  test("double multiplie par deux", () => {{
    expect(double(2)).toBe(4);
  }});

  test("suivant ajoute un", () => {{
    expect(suivant(1)).toBe(2);
  }});
  // {FIN}
}});
"""

GO_CODE = """package calc

// Double multiplie par deux.
func Double(x int) int {
	return 2 * x
}

// Suivant ajoute un, sauf au-delà de cent.
func Suivant(x int) int {
	if x > 100 {
		return x
	}
	return aide(x)
}

func aide(x int) int {
	return x + 1
}
"""
GO_TEST = f"""package calc

import "testing"

func TestDouble(t *testing.T) {{
	if got := Double(2); got != 4 {{
		t.Errorf("Double(2) = %d", got)
	}}
}}

func TestSuivant(t *testing.T) {{
	if got := Suivant(1); got != 2 {{
		t.Fatalf("Suivant(1) = %d", got)
	}}
}}

// {FIN}
"""

JAVA_POM = """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <groupId>essai</groupId>
  <artifactId>calc</artifactId>
  <version>1.0</version>
  <properties>
    <maven.compiler.release>17</maven.compiler.release>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
  </properties>
  <dependencies>
    <dependency>
      <groupId>org.junit.jupiter</groupId>
      <artifactId>junit-jupiter</artifactId>
      <version>5.10.2</version>
      <scope>test</scope>
    </dependency>
  </dependencies>
  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-surefire-plugin</artifactId>
        <version>3.2.5</version>
      </plugin>
      <plugin>
        <groupId>org.pitest</groupId>
        <artifactId>pitest-maven</artifactId>
        <version>1.15.8</version>
        <dependencies>
          <dependency>
            <groupId>org.pitest</groupId>
            <artifactId>pitest-junit5-plugin</artifactId>
            <version>1.2.1</version>
          </dependency>
        </dependencies>
        <configuration>
          <outputFormats><param>XML</param></outputFormats>
          <timestampedReports>false</timestampedReports>
        </configuration>
      </plugin>
    </plugins>
  </build>
</project>
"""
JAVA_CODE = """package essai;

public class Calc {
    public static int doubler(int x) {
        return 2 * x;
    }

    public static int suivant(int x) {
        if (x > 100) {
            return x;
        }
        return aide(x);
    }

    private static int aide(int x) {
        return x + 1;
    }
}
"""
JAVA_TEST = f"""package essai;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

class CalcTest {{
    @Test
    void doublerMultiplieParDeux() {{
        assertEquals(4, Calc.doubler(2));
    }}

    @Test
    void suivantAjouteUn() {{
        assertEquals(2, Calc.suivant(1));
    }}
    // {FIN}
}}
"""

KOTLIN_GRADLE = """plugins {
    kotlin("jvm") version "2.0.21"
    id("info.solidsoft.pitest") version "1.15.0"
}

repositories { mavenCentral() }

dependencies {
    testImplementation(kotlin("test"))
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.2")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

kotlin { jvmToolchain(21) }

tasks.test { useJUnitPlatform() }

pitest {
    junit5PluginVersion.set("1.2.1")
    targetClasses.set(listOf("essai.*"))
    outputFormats.set(listOf("XML"))
    timestampedReports.set(false)
}
"""
KOTLIN_CODE = """package essai

object Calc {
    fun doubler(x: Int): Int {
        return 2 * x
    }

    fun suivant(x: Int): Int {
        if (x > 100) {
            return x
        }
        return aide(x)
    }

    private fun aide(x: Int): Int {
        return x + 1
    }
}
"""
KOTLIN_TEST = f"""package essai

import kotlin.test.Test
import kotlin.test.assertEquals

class CalcTest {{
    @Test
    fun doublerMultiplieParDeux() {{
        assertEquals(4, Calc.doubler(2))
    }}

    @Test
    fun suivantAjouteUn() {{
        assertEquals(2, Calc.suivant(1))
    }}
    // {FIN}
}}
"""

RUBY_CODE = """# Le module de calcul d'essai.
module Calc
  def self.double(x)
    2 * x
  end

  def self.suivant(x)
    return x if x > 100

    aide(x)
  end

  def self.aide(x)
    x + 1
  end
  private_class_method :aide
end
"""
RUBY_TEST = f"""require_relative "../lib/calc"

RSpec.describe Calc do
  it "multiplie par deux" do
    expect(Calc.double(2)).to eq(4)
  end

  it "ajoute un" do
    expect(Calc.suivant(1)).to eq(2)
  end
  # {FIN}
end
"""

PHP_CODE = """<?php

namespace Essai;

final class Calc
{
    public static function double(int $x): int
    {
        return 2 * $x;
    }

    public static function suivant(int $x): int
    {
        if ($x > 100) {
            return $x;
        }
        return self::aide($x);
    }

    private static function aide(int $x): int
    {
        return $x + 1;
    }
}
"""
PHP_TEST = f"""<?php

namespace Essai\\Tests;

use Essai\\Calc;
use PHPUnit\\Framework\\TestCase;

final class CalcTest extends TestCase
{{
    public function testDouble(): void
    {{
        $this->assertSame(4, Calc::double(2));
    }}

    public function testSuivant(): void
    {{
        $this->assertSame(2, Calc::suivant(1));
    }}
    // {FIN}
}}
"""

# Une solution qui réunit le projet et ses tests : `dotnet build`, `dotnet
# test` et Stryker.NET la trouvent seuls à la racine.
CS_SOLUTION = """Microsoft Visual Studio Solution File, Format Version 12.00
# Visual Studio Version 17
VisualStudioVersion = 17.0.31903.59
MinimumVisualStudioVersion = 10.0.40219.1
Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "Calc", "src\\Calc\\Calc.csproj", "{2B3FC5AF-3300-41E2-9560-83BA67E993ED}"
EndProject
Project("{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}") = "Calc.Tests", "tests\\Calc.Tests\\Calc.Tests.csproj", "{519F2A7C-1914-45B0-85A5-B6D7E792B02B}"
EndProject
Global
\tGlobalSection(SolutionConfigurationPlatforms) = preSolution
\t\tDebug|Any CPU = Debug|Any CPU
\t\tRelease|Any CPU = Release|Any CPU
\tEndGlobalSection
\tGlobalSection(ProjectConfigurationPlatforms) = postSolution
\t\t{2B3FC5AF-3300-41E2-9560-83BA67E993ED}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
\t\t{2B3FC5AF-3300-41E2-9560-83BA67E993ED}.Debug|Any CPU.Build.0 = Debug|Any CPU
\t\t{2B3FC5AF-3300-41E2-9560-83BA67E993ED}.Release|Any CPU.ActiveCfg = Release|Any CPU
\t\t{2B3FC5AF-3300-41E2-9560-83BA67E993ED}.Release|Any CPU.Build.0 = Release|Any CPU
\t\t{519F2A7C-1914-45B0-85A5-B6D7E792B02B}.Debug|Any CPU.ActiveCfg = Debug|Any CPU
\t\t{519F2A7C-1914-45B0-85A5-B6D7E792B02B}.Debug|Any CPU.Build.0 = Debug|Any CPU
\t\t{519F2A7C-1914-45B0-85A5-B6D7E792B02B}.Release|Any CPU.ActiveCfg = Release|Any CPU
\t\t{519F2A7C-1914-45B0-85A5-B6D7E792B02B}.Release|Any CPU.Build.0 = Release|Any CPU
\tEndGlobalSection
EndGlobal
"""
CS_PROJET = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
  </PropertyGroup>
</Project>
"""
CS_PROJET_TESTS = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <IsPackable>false</IsPackable>
    <IsTestProject>true</IsTestProject>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.6.0" />
    <PackageReference Include="xunit" Version="2.4.2" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.4.5" />
  </ItemGroup>
  <ItemGroup>
    <ProjectReference Include="..\\..\\src\\Calc\\Calc.csproj" />
  </ItemGroup>
</Project>
"""
# Stryker.NET, épinglé dans le manifeste d'outils du projet : la version 5
# exige un SDK plus récent que .NET 8.
CS_OUTILS = json.dumps({"version": 1, "isRoot": True,
                        "tools": {"dotnet-stryker": {"version": "4.16.0", "commands": ["dotnet-stryker"]}}},
                       indent=2) + "\n"
CS_CODE = """namespace Calc;

public static class Calcul
{
    public static int Doubler(int x)
    {
        return 2 * x;
    }

    public static int Suivant(int x)
    {
        if (x > 100)
        {
            return x;
        }
        return Aide(x);
    }

    private static int Aide(int x)
    {
        return x + 1;
    }
}
"""
CS_TEST = f"""using Calc;
using Xunit;

namespace Calc.Tests;

public class CalcTests
{{
    [Fact]
    public void DoublerMultiplieParDeux()
    {{
        Assert.Equal(4, Calcul.Doubler(2));
    }}

    [Fact]
    public void SuivantAjouteUn()
    {{
        Assert.Equal(2, Calcul.Suivant(1));
    }}
    // {FIN}
}}
"""

LANGAGES = {
    "javascript": Langage(
        adaptateur="javascript",
        fichiers={
            "package.json": '{\n  "name": "calc", "version": "1.0.0", "type": "module", "private": true\n}\n',
            "stryker.config.json": '{\n  "testRunner": "vitest",\n  "mutate": ["src/**/*.js"],\n'
                                   '  "jsonReporter": { "fileName": "reports/mutation/mutation.json" }\n}\n',
            ".gitignore": "node_modules/\nreports/\n.stryker-tmp/\n",
            "src/calc.js": JS_CODE,
            "test/calc.test.js": JS_TEST,
        },
        preparer=["npm install --no-audit --no-fund --save-dev vitest@3 @stryker-mutator/core@8 "
                  "@stryker-mutator/vitest-runner@8"],
        code="src/calc.js",
        creux=("test/calc.test.js", f"  // {FIN}\n", '  test("ne mesure rien", () => {\n    double(3);\n  });\n'),
        desactive=("test/calc.test.js", f"  // {FIN}\n",
                   '  test.skip("plus tard", () => {\n    expect(double(3)).toBe(6);\n  });\n'),
        attendu=("test/calc.test.js", "toBe(4)", "toBe(5)"),
        fonction=("src/calc.js", "function aide(x) {", "export function quadruple(x) {\n  return 4 * x;\n}\n\n"
                                                      "function aide(x) {"),
        bogue=("src/calc.js", "return 2 * x;", "return 2 * x + 1;"),
        regression=("test/regression.test.js", 'import { expect, test } from "vitest";\nimport { double } from '
                    '"../src/calc.js";\n\ntest("double de trois", () => {\n  expect(double(3)).toBe(6);\n});\n'),
    ),
    "go": Langage(
        adaptateur="go",
        fichiers={"go.mod": "module example.com/calc\n\ngo 1.22\n", ".gitignore": "gremlins.json\n",
                  "calc.go": GO_CODE, "calc_test.go": GO_TEST},
        preparer=["go install github.com/go-gremlins/gremlins/cmd/gremlins@latest"],
        code="calc.go",
        creux=("calc_test.go", f"// {FIN}\n", "func TestRien(t *testing.T) {\n\t_ = Double(3)\n}\n"),
        desactive=("calc_test.go", f"// {FIN}\n", "func TestPlusTard(t *testing.T) {\n\tt.Skip()\n"
                                                 "\tif Double(3) != 6 {\n\t\tt.Fatal(\"non\")\n\t}\n}\n"),
        attendu=("calc_test.go", "got != 4", "got != 5"),
        fonction=("calc.go", "func aide(x int) int {", "// Quadruple multiplie par quatre.\n"
                                                      "func Quadruple(x int) int {\n\treturn 4 * x\n}\n\n"
                                                      "func aide(x int) int {"),
        bogue=("calc.go", "return 2 * x\n", "return 2*x + 1\n"),
        regression=("regression_test.go", 'package calc\n\nimport "testing"\n\nfunc TestDoubleDeTrois(t *testing.T) {\n'
                    '\tif got := Double(3); got != 6 {\n\t\tt.Errorf("Double(3) = %d", got)\n\t}\n}\n'),
        env={"PATH": f"{Path.home() / 'go/bin'}{os.pathsep}{os.environ.get('PATH', '')}"},
    ),
    "java": Langage(
        adaptateur="java",
        fichiers={"pom.xml": JAVA_POM, ".gitignore": "target/\n", "src/main/java/essai/Calc.java": JAVA_CODE,
                  "src/test/java/essai/CalcTest.java": JAVA_TEST},
        preparer=["mvn -q -B test-compile"],
        code="src/main/java/essai/Calc.java",
        creux=("src/test/java/essai/CalcTest.java", f"    // {FIN}\n",
               "    @Test\n    void neMesureRien() {\n        Calc.doubler(3);\n    }\n"),
        desactive=("src/test/java/essai/CalcTest.java", f"    // {FIN}\n",
                   "    @Test\n    @Disabled\n    void plusTard() {\n        assertEquals(6, Calc.doubler(3));\n    }\n"),
        attendu=("src/test/java/essai/CalcTest.java", "assertEquals(4,", "assertEquals(5,"),
        fonction=("src/main/java/essai/Calc.java", "    private static int aide(int x) {",
                  "    public static int quadrupler(int x) {\n        return 4 * x;\n    }\n\n"
                  "    private static int aide(int x) {"),
        bogue=("src/main/java/essai/Calc.java", "return 2 * x;", "return 2 * x + 1;"),
        regression=("src/test/java/essai/RegressionTest.java",
                    "package essai;\n\nimport static org.junit.jupiter.api.Assertions.assertEquals;\n\n"
                    "import org.junit.jupiter.api.Test;\n\nclass RegressionTest {\n    @Test\n"
                    "    void doublerDeTrois() {\n        assertEquals(6, Calc.doubler(3));\n    }\n}\n"),
    ),
    "kotlin": Langage(
        adaptateur="kotlin",
        fichiers={"settings.gradle.kts": 'rootProject.name = "essai"\n', "build.gradle.kts": KOTLIN_GRADLE,
                  ".gitignore": "build/\n.gradle/\n.kotlin/\n", "src/main/kotlin/essai/Calc.kt": KOTLIN_CODE,
                  "src/test/kotlin/essai/CalcTest.kt": KOTLIN_TEST},
        preparer=["gradle -q --no-daemon wrapper", "./gradlew -q testClasses"],
        code="src/main/kotlin/essai/Calc.kt",
        creux=("src/test/kotlin/essai/CalcTest.kt", f"    // {FIN}\n",
               "    @Test\n    fun neMesureRien() {\n        Calc.doubler(3)\n    }\n"),
        desactive=("src/test/kotlin/essai/CalcTest.kt", f"    // {FIN}\n",
                   "    @kotlin.test.Ignore\n    @Test\n    fun plusTard() {\n        assertEquals(6, Calc.doubler(3))\n"
                   "    }\n"),
        attendu=("src/test/kotlin/essai/CalcTest.kt", "assertEquals(4,", "assertEquals(5,"),
        fonction=("src/main/kotlin/essai/Calc.kt", "    private fun aide(x: Int): Int {",
                  "    fun quadrupler(x: Int): Int {\n        return 4 * x\n    }\n\n"
                  "    private fun aide(x: Int): Int {"),
        bogue=("src/main/kotlin/essai/Calc.kt", "return 2 * x\n", "return 2 * x + 1\n"),
        regression=("src/test/kotlin/essai/RegressionTest.kt",
                    "package essai\n\nimport kotlin.test.Test\nimport kotlin.test.assertEquals\n\n"
                    "class RegressionTest {\n    @Test\n    fun doublerDeTrois() {\n"
                    "        assertEquals(6, Calc.doubler(3))\n    }\n}\n"),
    ),
    "ruby": Langage(
        adaptateur="ruby",
        fichiers={"Gemfile": 'source "https://rubygems.org"\n\ngem "rspec", "~> 3.13"\ngem "mutant-rspec", "~> 0.12"\n',
                  ".gitignore": "vendor/\n.bundle/\n.mutant/\n", "lib/calc.rb": RUBY_CODE,
                  "mutant.yml": "usage: opensource\nintegration:\n  name: rspec\nincludes:\n  - lib\nrequires:\n"
                                "  - ./lib/calc.rb\nmatcher:\n  subjects:\n    - Calc*\n",
                  "spec/calc_spec.rb": RUBY_TEST},
        preparer=["bundle config set --local path vendor/bundle", "bundle install --quiet"],
        code="lib/calc.rb",
        creux=("spec/calc_spec.rb", f"  # {FIN}\n", '  it "ne mesure rien" do\n    Calc.double(3)\n  end\n'),
        desactive=("spec/calc_spec.rb", f"  # {FIN}\n", '  xit "plus tard" do\n    expect(Calc.double(3)).to eq(6)\n  end\n'),
        attendu=("spec/calc_spec.rb", "to eq(4)", "to eq(5)"),
        fonction=("lib/calc.rb", "  def self.aide(x)", "  def self.quadruple(x)\n    4 * x\n  end\n\n  def self.aide(x)"),
        bogue=("lib/calc.rb", "    2 * x\n", "    2 * x + 1\n"),
        regression=("spec/regression_spec.rb", 'require_relative "../lib/calc"\n\nRSpec.describe Calc do\n'
                    '  it "double trois" do\n    expect(Calc.double(3)).to eq(6)\n  end\nend\n'),
    ),
    "php": Langage(
        adaptateur="php",
        fichiers={
            "composer.json": json.dumps({"name": "essai/calc", "autoload": {"psr-4": {"Essai\\": "src/"}},
                                         "config": {"allow-plugins": {"infection/extension-installer": True}}},
                                        indent=2) + "\n",
            "phpunit.xml": '<?xml version="1.0" encoding="UTF-8"?>\n<phpunit bootstrap="vendor/autoload.php">\n'
                           '  <testsuites><testsuite name="essai"><directory>tests</directory></testsuite></testsuites>\n'
                           '  <source><include><directory>src</directory></include></source>\n</phpunit>\n',
            "infection.json5": '{\n  "source": {"directories": ["src"]},\n  "logs": {"json": "infection.json"},\n'
                               '  "phpUnit": {"customPath": "vendor/bin/phpunit"}\n}\n',
            ".gitignore": "vendor/\ninfection.json\n.phpunit.cache/\n",
            "src/Calc.php": PHP_CODE, "tests/CalcTest.php": PHP_TEST},
        preparer=["composer require --dev --no-interaction --quiet phpunit/phpunit:^10.5 infection/infection:^0.29"],
        code="src/Calc.php",
        creux=("tests/CalcTest.php", f"    // {FIN}\n",
               "    public function testRien(): void\n    {\n        Calc::double(3);\n    }\n"),
        desactive=("tests/CalcTest.php", f"    // {FIN}\n", "    public function testPlusTard(): void\n    {\n"
                   "        $this->markTestSkipped();\n        $this->assertSame(6, Calc::double(3));\n    }\n"),
        attendu=("tests/CalcTest.php", "assertSame(4,", "assertSame(5,"),
        fonction=("src/Calc.php", "    private static function aide(int $x): int",
                  "    public static function quadruple(int $x): int\n    {\n        return 4 * $x;\n    }\n\n"
                  "    private static function aide(int $x): int"),
        bogue=("src/Calc.php", "return 2 * $x;", "return 2 * $x + 1;"),
        regression=("tests/RegressionTest.php", "<?php\n\nnamespace Essai\\Tests;\n\nuse Essai\\Calc;\n"
                    "use PHPUnit\\Framework\\TestCase;\n\nfinal class RegressionTest extends TestCase\n{\n"
                    "    public function testDoubleDeTrois(): void\n    {\n"
                    "        $this->assertSame(6, Calc::double(3));\n    }\n}\n"),
    ),
    "csharp": Langage(
        adaptateur="csharp",
        fichiers={"Calc.sln": CS_SOLUTION, ".gitignore": "bin/\nobj/\nStrykerOutput/\n",
                  ".config/dotnet-tools.json": CS_OUTILS, "src/Calc/Calc.csproj": CS_PROJET,
                  "src/Calc/Calc.cs": CS_CODE, "tests/Calc.Tests/Calc.Tests.csproj": CS_PROJET_TESTS,
                  "tests/Calc.Tests/CalcTests.cs": CS_TEST},
        preparer=["dotnet restore", "dotnet tool restore"],
        code="src/Calc/Calc.cs",
        creux=("tests/Calc.Tests/CalcTests.cs", f"    // {FIN}\n",
               "    [Fact]\n    public void NeMesureRien()\n    {\n        Calcul.Doubler(3);\n    }\n"),
        # xUnit ne désactive un test que par sa raison : vide, elle n'en dit aucune.
        desactive=("tests/Calc.Tests/CalcTests.cs", f"    // {FIN}\n",
                   '    [Fact(Skip = "")]\n    public void PlusTard()\n    {\n'
                   "        Assert.Equal(6, Calcul.Doubler(3));\n    }\n"),
        attendu=("tests/Calc.Tests/CalcTests.cs", "Assert.Equal(4,", "Assert.Equal(5,"),
        fonction=("src/Calc/Calc.cs", "    private static int Aide(int x)",
                  "    public static int Quadrupler(int x)\n    {\n        return 4 * x;\n    }\n\n"
                  "    private static int Aide(int x)"),
        bogue=("src/Calc/Calc.cs", "return 2 * x;", "return 2 * x + 1;"),
        regression=("tests/Calc.Tests/RegressionTests.cs",
                    "using Calc;\nusing Xunit;\n\nnamespace Calc.Tests;\n\npublic class RegressionTests\n{\n"
                    "    [Fact]\n    public void DoublerDeTrois()\n    {\n"
                    "        Assert.Equal(6, Calcul.Doubler(3));\n    }\n}\n"),
        env={"DOTNET_CLI_TELEMETRY_OPTOUT": "1", "DOTNET_NOLOGO": "1"},
    ),
}


# --------------------------------------------------------------------------
# Le déroulé
# --------------------------------------------------------------------------


class Projet:
    def __init__(self, dossier: Path, langage: Langage):
        self.d = dossier
        self.l = langage
        self.env = {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "GIT_"))}
        self.env.update({"GIT_AUTHOR_NAME": "essai", "GIT_AUTHOR_EMAIL": "essai@exemple.org",
                         "GIT_COMMITTER_NAME": "essai", "GIT_COMMITTER_EMAIL": "essai@exemple.org",
                         "GIT_CONFIG_NOSYSTEM": "1", **langage.env})

    def run(self, commande: str | list[str], delai: int = 1200) -> subprocess.CompletedProcess:
        return subprocess.run(commande, shell=isinstance(commande, str), cwd=self.d, env=self.env,
                              capture_output=True, text=True, timeout=delai)

    def git(self, *args: str) -> str:
        r = self.run(["git", *args])
        if r.returncode:
            raise RuntimeError(f"git {' '.join(args)} : {r.stderr.strip()}")
        return r.stdout.strip()

    def socle(self, *args: str) -> subprocess.CompletedProcess:
        return self.run([sys.executable, str(self.d / ".socle/socle"), *args])

    def commit(self, message: str):
        self.git("add", "-A")
        self.git("commit", "-q", "--no-verify", "-m", message)
        return self.git("rev-parse", "HEAD")

    def remplacer(self, quoi: tuple[str, str, str]):
        fichier, avant, apres = quoi
        p = self.d / fichier
        texte = p.read_text()
        if avant not in texte:
            raise RuntimeError(f"{fichier} : « {avant.strip()} » introuvable")
        # Un ajout avant le marqueur de fin le garde ; un remplacement le remplace.
        p.write_text(texte.replace(avant, apres + avant if FIN in avant else apres, 1))

    def plafond(self, n: int):
        gf = self.d / ".socle/guardrails.toml"
        texte = gf.read_text()
        debut = texte.index("[mutation.caps]\n") + len("[mutation.caps]\n")
        fin = texte.find("\n[", debut)
        fin = len(texte) if fin == -1 else fin + 1
        gf.write_text(texte[:debut] + f'"{self.l.code}" = {{ max = {n}, reason = "mesuré par le banc des adaptateurs" }}\n'
                      + texte[fin:])


def refuse_par(sortie: str, controle: str) -> bool:
    for ligne in sortie.splitlines():
        if ligne.startswith("ECHEC — ") and " : " in ligne:
            return controle in [x.strip() for x in ligne.split(" : ", 1)[1].split(",")]
    return False


def eprouver(nom: str, dossier: Path, bavard: bool) -> dict:
    l = LANGAGES[nom]
    p = Projet(dossier, l)
    res: dict = {"langage": nom, "etapes": {}}

    def noter(etape: str, ok: bool, detail: str = ""):
        res["etapes"][etape] = {"ok": ok, "detail": detail.strip()[-1500:]}
        if bavard:
            print(f"  {'ok ' if ok else 'ÉCHEC'} {nom} — {etape}" + ("" if ok else f"\n{detail.strip()[-1500:]}"),
                  file=sys.stderr)

    dossier.mkdir(parents=True)
    for rel, contenu in l.fichiers.items():
        (dossier / rel).parent.mkdir(parents=True, exist_ok=True)
        (dossier / rel).write_text(contenu)
    p.git("init", "-q", "-b", "main")
    for c in l.preparer:
        r = p.run(c)
        if r.returncode:
            noter("dépendances", False, r.stdout + r.stderr)
            return res
    noter("dépendances", True)
    r = p.run([sys.executable, "-c", "import sys; sys.path.insert(0, sys.argv[1]); from socle.cli import main; "
               "sys.exit(main(sys.argv[2:]))", str(MOTEUR), "install", "--target", ".", "--adapter", "auto",
               "--owner", "@essai"])
    adaptateur = (dossier / ".socle/adapter.toml").read_text() if (dossier / ".socle/adapter.toml").is_file() else ""
    noter("installation, adaptateur déduit du dépôt", f'language = "{l.adaptateur}"' in adaptateur, r.stdout + r.stderr)
    p.plafond(99)
    base = p.commit("Projet d'essai")

    r = p.socle("verify", "--fast")
    noter("verify sur le projet sain", r.returncode == 0, r.stdout + r.stderr)

    for etape, quoi, controle in (("test sans assertion", l.creux, "tests.creux"),
                                  ("test désactivé sans raison", l.desactive, "tests.creux"),
                                  ("valeur attendue changée", l.attendu, "tests.attendus"),
                                  ("fonction publique sans test", l.fonction, "tests.code-teste")):
        p.remplacer(quoi)
        r = p.socle("check", "--stage", "agent", "--base", "HEAD", "--only", controle)
        noter(f"{etape} refusé par {controle}", refuse_par(r.stdout, controle), r.stdout + r.stderr)
        p.git("checkout", "--", ".")

    # Un correctif qui livre son test de régression, puis un qui n'en livre pas.
    p.remplacer(l.bogue)
    avant = p.commit("Un bogue entre")
    p.git("checkout", base, "--", l.bogue[0])
    chemin, contenu = l.regression
    (dossier / chemin).parent.mkdir(parents=True, exist_ok=True)
    (dossier / chemin).write_text(contenu)
    p.commit("fix: double redevient juste")
    r = p.socle("check", "--stage", "ci", "--base", avant, "--only", "tests.regression")
    noter("correctif avec son test de régression, rejoué sur le parent", r.returncode == 0, r.stdout + r.stderr)
    milieu = p.git("rev-parse", "HEAD")
    p.remplacer(l.bogue)
    p.commit("fix: rien de prouvé")
    r = p.socle("check", "--stage", "ci", "--base", milieu, "--only", "tests.regression")
    noter("correctif sans test refusé par tests.regression", refuse_par(r.stdout, "tests.regression"), r.stdout + r.stderr)
    p.git("reset", "-q", "--hard", milieu)

    # La mutation : le balayage, son rapport, le verdict au plafond mesuré.
    import tomllib

    cap = tomllib.loads(adaptateur)["capabilities"]["mutation"]
    debut = time.time()
    r = p.run(cap["command"], delai=1800)
    res["mutation_secondes"] = round(time.time() - debut, 1)
    compte = mutation.LECTEURS[cap["parser"]](dossier).get(l.code)
    res["mutation"] = dict(compte or {})
    noter("balayage de mutation lu", bool(compte), "" if compte else r.stdout + r.stderr)
    if compte:
        n = compte["survivants"]
        p.plafond(n)
        r = p.socle("mutation-verdict", ".")
        noter(f"verdict au plafond mesuré ({n} survivant(s))", r.returncode == 0, r.stdout + r.stderr)
        if n:
            p.plafond(n - 1)
            r = p.socle("mutation-verdict", ".")
            noter("verdict sous le plafond refusé", r.returncode != 0, r.stdout + r.stderr)
    res["reussi"] = all(e["ok"] for e in res["etapes"].values())
    return res


# Un projet en deux langages, comme JustCook : ses outils en Python sous
# pytest, son app en Kotlin sous Gradle (ADR-0051, point 8).
MIXTE = "python+kotlin"
PY_PYPROJECT = """[project]
name = "outils"
version = "0.1.0"

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]

[tool.mutmut]
source_paths = ["src/outils"]
pytest_add_cli_args_test_selection = ["tests"]
"""
PY_CODE = "def tripler(x):\n    return 3 * x\n"
PY_TEST = "from outils.calc import tripler\n\n\ndef test_tripler():\n    assert tripler(2) == 6\n"
PY_REGRESSION = ("tests/test_regression.py",
                 "from outils.calc import tripler\n\n\ndef test_tripler_de_trois():\n    assert tripler(3) == 9\n")
PY_MODULE = "src/outils/calc.py"


def eprouver_mixte(dossier: Path, bavard: bool) -> dict:
    """Le projet en Python et en Kotlin : chaque langage jugé par son
    adaptateur, avec ses vrais outils (pytest et mutmut, Gradle et PIT)."""
    k = LANGAGES["kotlin"]
    p = Projet(dossier, k)
    res: dict = {"langage": MIXTE, "etapes": {}}

    def noter(etape: str, ok: bool, detail: str = ""):
        res["etapes"][etape] = {"ok": ok, "detail": detail.strip()[-1500:]}
        if bavard:
            print(f"  {'ok ' if ok else 'ÉCHEC'} {MIXTE} — {etape}" + ("" if ok else f"\n{detail.strip()[-1500:]}"),
                  file=sys.stderr)

    fichiers = {**k.fichiers, "pyproject.toml": PY_PYPROJECT, PY_MODULE: PY_CODE, "src/outils/__init__.py": "",
                "tests/test_outils.py": PY_TEST}
    fichiers[".gitignore"] += "mutants/\nmutmut-results.txt\n__pycache__/\n.pytest_cache/\n"
    dossier.mkdir(parents=True)
    for rel, contenu in fichiers.items():
        (dossier / rel).parent.mkdir(parents=True, exist_ok=True)
        (dossier / rel).write_text(contenu)
    p.git("init", "-q", "-b", "main")
    for c in [*k.preparer, f"{sys.executable} -m pytest -q --co"]:
        r = p.run(c)
        if r.returncode:
            noter("dépendances", False, r.stdout + r.stderr)
            return res
    noter("dépendances", True)
    r = p.run([sys.executable, "-c", "import sys; sys.path.insert(0, sys.argv[1]); from socle.cli import main; "
               "sys.exit(main(sys.argv[2:]))", str(MOTEUR), "install", "--target", ".", "--adapter", "auto",
               "--owner", "@essai"])
    principal = (dossier / ".socle/adapter.toml").read_text() if (dossier / ".socle/adapter.toml").is_file() else ""
    noter("installation, un adaptateur par langage déduit du dépôt",
          'language = "python"' in principal and (dossier / ".socle/adapters/kotlin.toml").is_file(),
          r.stdout + r.stderr)
    caps = {PY_MODULE: 99, k.code: 99}

    def plafonds():
        gf = dossier / ".socle/guardrails.toml"
        texte = gf.read_text()
        debut = texte.index("[mutation.caps]\n") + len("[mutation.caps]\n")
        fin = texte.find("\n[", debut)
        fin = len(texte) if fin == -1 else fin + 1
        gf.write_text(texte[:debut] + "".join(f'"{m}" = {{ max = {n}, reason = "mesuré par le banc des adaptateurs" }}\n'
                                              for m, n in caps.items()) + texte[fin:])

    plafonds()
    base = p.commit("Projet d'essai en deux langages")

    r = p.socle("verify", "--fast")
    noter("verify sur le projet sain, les étapes des deux adaptateurs",
          r.returncode == 0 and "verify.kotlin.tests" in r.stdout + r.stderr and "verify.python.tests" in r.stdout + r.stderr,
          r.stdout + r.stderr)
    r = p.socle("check", "--stage", "agent", "--base", "HEAD", "--only", "adaptateur.recouvrement")
    noter("aucun fichier désigné par les deux adaptateurs", r.returncode == 0, r.stdout + r.stderr)

    for etape, quoi, prefixe in (("test Kotlin sans assertion", k.creux, "kotlin : "),
                                 ("test Python sans assertion",
                                  ("tests/test_outils.py", "    assert tripler(2) == 6\n", "    tripler(2)\n"),
                                  "python : ")):
        p.remplacer(quoi)
        r = p.socle("check", "--stage", "agent", "--base", "HEAD", "--only", "tests.creux")
        noter(f"{etape} refusé par tests.creux, qui nomme son adaptateur",
              refuse_par(r.stdout, "tests.creux") and prefixe in r.stdout, r.stdout + r.stderr)
        p.git("checkout", "--", ".")

    # Un correctif du code Kotlin ne se prouve pas par un test Python.
    p.remplacer(k.bogue)
    avant = p.commit("Un bogue entre dans le code Kotlin")
    p.git("checkout", base, "--", k.bogue[0])
    (dossier / PY_REGRESSION[0]).write_text(PY_REGRESSION[1])
    p.commit("fix: doubler redevient juste")
    r = p.socle("check", "--stage", "ci", "--base", avant, "--only", "tests.regression")
    noter("correctif Kotlin prouvé par un seul test Python refusé par tests.regression",
          refuse_par(r.stdout, "tests.regression") and "kotlin : " in r.stdout and "python : " not in r.stdout,
          r.stdout + r.stderr)
    p.git("reset", "-q", "--hard", avant)
    p.git("checkout", base, "--", k.bogue[0])
    chemin, contenu = k.regression
    (dossier / chemin).write_text(contenu)
    p.commit("fix: doubler redevient juste")
    r = p.socle("check", "--stage", "ci", "--base", avant, "--only", "tests.regression")
    noter("correctif Kotlin avec son test Kotlin, rejoué sur le parent", r.returncode == 0, r.stdout + r.stderr)

    # La mutation : chaque adaptateur balaie ses modules avec son outil.
    debut = time.time()
    r = p.socle("mutation-run")
    res["mutation_secondes"] = round(time.time() - debut, 1)
    sortie = r.stdout + r.stderr
    vus = {m: (f"{m} :" in sortie and "aucun résultat" not in sortie.split(m, 1)[1].splitlines()[0]) for m in caps}
    res["mutation"] = {"python": mutation.LECTEURS["mutmut"](dossier).get(PY_MODULE),
                       "kotlin": mutation.LECTEURS["pit"](dossier).get(k.code)}
    res["mutation"] = {n: dict(c or {}) for n, c in res["mutation"].items()}
    noter("balayage de mutation des deux adaptateurs, chacun au plafond de ses modules",
          r.returncode == 0 and all(vus.values()) and all(res["mutation"].values()), sortie)
    res["reussi"] = all(e["ok"] for e in res["etapes"].values())
    return res


def rapport(resultats: list[dict]) -> str:
    lignes = ["# Banc des adaptateurs", "", "Chaque adaptateur, éprouvé sur un projet jetable de son langage "
              "(`bench/adapters.py`).", ""]
    for r in resultats:
        lignes += [f"## {r['langage']} — {'réussi' if r.get('reussi') else 'ÉCHEC'}", ""]
        for etape, e in r["etapes"].items():
            lignes.append(f"- {'ok' if e['ok'] else '**ÉCHEC**'} — {etape}")
        if "mutation" in r:
            lignes += ["", f"Mutation : {r['mutation']} en {r.get('mutation_secondes')} s."]
        lignes.append("")
    return "\n".join(lignes)


def main(argv=None) -> int:
    a = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    a.add_argument("--langages", default=",".join([*LANGAGES, MIXTE]),
                   help=f"les langages à éprouver, et `{MIXTE}` pour le projet en deux langages")
    a.add_argument("--garder", action="store_true", help="garder les projets jetables")
    a.add_argument("--sortie", help="dossier où écrire rapport.md et resultats.json")
    args = a.parse_args(argv)
    racine = Path(tempfile.mkdtemp(prefix="socle-banc-adaptateurs-"))
    resultats = []
    try:
        for nom in [x.strip() for x in args.langages.split(",") if x.strip()]:
            print(f"{nom} …", file=sys.stderr)
            try:
                resultats.append(eprouver_mixte(racine / "mixte", True) if nom == MIXTE
                                 else eprouver(nom, racine / nom, True))
            except Exception as e:  # un banc qui plante le dit, il ne passe pas
                resultats.append({"langage": nom, "etapes": {"déroulé": {"ok": False, "detail": f"{type(e).__name__}: {e}"}},
                                  "reussi": False})
    finally:
        if args.garder:
            print(f"projets gardés dans {racine}", file=sys.stderr)
        else:
            shutil.rmtree(racine, ignore_errors=True)
    texte = rapport(resultats)
    print(texte)
    if args.sortie:
        s = Path(args.sortie)
        s.mkdir(parents=True, exist_ok=True)
        (s / "rapport.md").write_text(texte)
        (s / "resultats.json").write_text(json.dumps(resultats, ensure_ascii=False, indent=2))
    return 0 if all(r.get("reussi") for r in resultats) else 1


if __name__ == "__main__":
    sys.exit(main())
