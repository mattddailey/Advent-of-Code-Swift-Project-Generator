#!/usr/bin/env python3

import os
import sys
import subprocess
from pathlib import Path

def write(path: Path, contents: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents, encoding="utf-8")

def package_swift(project_name: str):
    return f"""// swift-tools-version: 6.0

import PackageDescription

let package = Package(
  name: "{project_name}",
  platforms: [.macOS(.v13)],
  products: [
    .executable(name: "{project_name}", targets: ["{project_name}"])
  ],
  dependencies: [
    .package(url: "https://github.com/apple/swift-argument-parser.git", from: "1.3.0")
  ],
  targets: [
    .executableTarget(
      name: "{project_name}",
      dependencies: [.product(name: "ArgumentParser", package: "swift-argument-parser")],
      resources: [.copy("Inputs")]
    ),
    .testTarget(
      name: "{project_name}Tests",
      dependencies: ["{project_name}"]
    )
  ]
)
"""

def gitignore_contents():
    return """# Swift Package Manager
.build/
.swiftpm/
Package.resolved

# Xcode
.DS_Store
xcuserdata/
DerivedData/
*.xcworkspace
*.xcodeproj

# Logs
*.log

# Advent of Code Inputs
Inputs/
"""

def protocol_file(year: int):
    return f"""import ArgumentParser
import Foundation

protocol AdventOfCodeDay: AsyncParsableCommand {{
  static var day: Int {{ get }}

  func parse(_ input: String) async throws -> String
  func part1(_ input: String) async throws -> String
  func part2(_ input: String) async throws -> String
}}

extension AdventOfCodeDay {{
  static var configuration: CommandConfiguration {{
    .init(
      commandName: "day\\(Self.day)",
      abstract: "Run Advent of Code Day \\(Self.day)"
    )
  }}

  mutating func run() async throws {{
    let input = try await input(day: Self.day)
    let parsed = try await parse(input)
    let part1 = try await part1(parsed)
    let part2 = try await part2(parsed)
    print("Part 1: \(part1)")
    print("Part 2: \(part2)")
  }}

  private func input(day: Int) async throws -> String {{
    let fileName = "day" + String(format: "%02d", day) + ".txt"
    
    guard let fileURL = Bundle.module.url(forResource: fileName, withExtension: nil, subdirectory: "Inputs") else {{
      return try await remoteInput(day: day)
    }}
    
    let inputFileString = try String(contentsOf: fileURL, encoding: .utf8)
    
    guard !inputFileString.isEmpty else {{
      return try await remoteInput(day: day)
    }}
    
    print("Using local input for day \(day)")
    return inputFileString
  }}
  
  private func remoteInput(day: Int) async throws -> String {{
    print("Downloading input for day \(day)...")
    
    guard let session = ProcessInfo.processInfo.environment["AOC_SESSION"], !session.isEmpty else {{
      fatalError("Please set your AOC_SESSION environment variable to your Advent of Code session cookie.")
    }}
    
    guard let url = URL(string: "https://adventofcode.com/{year}/day/\(day)/input") else {{
      fatalError("Failed to construct input URL for day \(day), year {year}")
    }}
    
    var request = URLRequest(url: url)
    request.setValue("session=\(session)", forHTTPHeaderField: "Cookie")

    let (data, response) = try await URLSession.shared.data(for: request)

    guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {{
      fatalError("Failed to download input for day \(day)")
    }}

    guard let downloadedString = String(data: data, encoding: .utf8) else {{
      fatalError("Unable to decode downloaded input data for day \(day)")
    }}
    
    return downloadedString
  }}
}}
"""

def root_cli(subcommands, year: int):
    subs = ",\n      ".join(subcommands)
    struct_name = f"AdventOfCode{year}"
    cmd_name = f"aoc-{year}"
    return f"""import ArgumentParser

@main
struct {struct_name}: AsyncParsableCommand {{
  static let configuration: CommandConfiguration = .init(
    commandName: "{cmd_name}",
    abstract: "Run Advent of Code solutions for {year}",
    subcommands: [
      {subs}
    ]
  )
}}
"""

def day_file(day: int):
    return f"""import ArgumentParser

struct Day{day:02d}: AdventOfCodeDay {{
  static let day = {day}

  func parse(_ input: String) async throws -> String {{
    input.trimmingCharacters(in: .whitespacesAndNewlines)
  }}

  func part1(_ input: String) async throws -> String {{
    "Not implemented"
  }}

  func part2(_ input: String) async throws -> String {{
    "Not implemented"
  }}
}}
"""

def test_file(day: int, project_name: str):
    return f"""import Testing
@testable import {project_name}

struct Day{day:02d}Tests {{
  let sample = \"\"\"
  \"\"\"

  @Test
  func testParse() async throws {{
    let day = Day{day:02d}()
    let parsed = try await day.parse(sample)
    #expect(parsed.isEmpty == false)
  }}

  @Test
  func testPart1() async throws {{
    let day = Day{day:02d}()
    let parsed = try await day.parse(sample)
    let result = try await day.part1(parsed)
    #expect(result == "Not implemented")
  }}

  @Test
  func testPart2() async throws {{
    let day = Day{day:02d}()
    let parsed = try await day.parse(sample)
    let result = try await day.part2(parsed)
    #expect(result == "Not implemented")
  }}
}}
"""

def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_aoc_project.py <year> <number_of_days>")
        sys.exit(1)

    year = int(sys.argv[1])
    days = int(sys.argv[2])
    project_name = f"AdventOfCode{year}"

    root = Path(os.getcwd())
    project_dir = root / project_name
    sources = project_dir / "Sources" / project_name
    tests = project_dir / "Tests" / f"{project_name}Tests"
    inputs = sources / "Inputs"

    write(project_dir / "Package.swift", package_swift(project_name))
    write(project_dir / ".gitignore", gitignore_contents())

    write(sources / "AdventOfCodeDay.swift", protocol_file(year))

    subcommands = []
    for day in range(1, days + 1):
        struct_name = f"Day{day:02d}"
        subcommands.append(f"{struct_name}.self")

        write(sources / f"{struct_name}.swift", day_file(day))
        write(tests / f"{struct_name}Tests.swift", test_file(day, project_name))
        write(inputs / f"day{day:02d}.txt", "")

    write(sources / "AdventOfCode.swift", root_cli(subcommands, year))

    try:
        subprocess.run(["git", "init"], cwd=project_dir, check=True)
        subprocess.run(["git", "add", "."], cwd=project_dir, check=True)
        subprocess.run(
            ["git", "commit", "-m", f"Initial Advent of Code {year} project"],
            cwd=project_dir,
            check=True,
        )
        print("Initialized git repository.")
    except Exception as e:
        print("Warning: Git initialization failed:", e)

    print(f"Generated Advent of Code Swift project for {year} with {days} days!")

if __name__ == "__main__":
    main()