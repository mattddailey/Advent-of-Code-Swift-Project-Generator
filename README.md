# Advent of Code Swift Project Generator

This repository contains a Python script that automatically generates a full **Advent of Code** project written in Swift.  
It creates:

- A fully configured Swift Package
- A root CLI command using **swift-argument-parser**
- One subcommand per day (`day01`, `day02`, …)
- A shared `AdventOfCodeDay` protocol
- Boilerplate implementation for each day
- Unit tests using **Swift Testing**
- Input files for each day under `Inputs/`

This tool lets you instantly scaffold an entire AoC project for any year.

---

## ✨ Features

- Generates a standalone Swift package named:  
  **`AdventOfCode<YEAR>`**
- Automatically sets CLI command name to:  
  **`aoc-<year>`**
- Each day is a subcommand (e.g., `aoc-2025 day07`)
- Reads puzzle inputs from `Inputs/dayXX.txt`
- Includes Swift Testing templates with sample input placeholders
- Structured, uniform file layout
- Designed for Swift 6

---

## 📦 Requirements

- Python 3.8+
- Swift 6+
- macOS (for Swift toolchain compatibility)

---

## 🚀 Usage

From the directory where you want to generate the project, run:

```bash
python generate_aoc_project.py <year> <number_of_days>
