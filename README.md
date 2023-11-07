# OoO-Simulator
This project implements an out-of-order CPU and evaluates the impact of various architectural parameters on CPU performance
Creating a README file for your project is essential for providing information and instructions to users and contributors. Here's a sample README.md file for your project, based on the code you provided:

```markdown
# OoO-Simulator

OoO-Simulator is a project that implements an out-of-order CPU and evaluates the impact of various architectural parameters on CPU performance.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Usage](#usage)
- [Project Structure](#project-structure)

## Overview

This project is a simulator for an out-of-order CPU, designed to assess the effect of architectural choices on CPU behavior and performance. It provides a flexible platform for experimenting with different CPU architectures and parameters.

## Features

- Out-of-order CPU simulation.
- Evaluation of architectural choices.
- Support for various CPU components, such as instruction execution units, reorder buffer, and branch prediction.
- Ability to customize the CPU's configuration and parameters.

## Usage

To run the OoO-Simulator, follow these steps:

1. Clone the repository to your local machine:

   ```
   git clone https://github.com/Fatemehgolshan/OoO-Simulator.git
   cd OoO-Simulator
   ```


2. Configure the simulation by providing a configuration file and input code file as command-line arguments:

   ```
   python processor.py path/to/config/file path/to/input/code
   ```

3. The simulator will execute the code and evaluate CPU performance based on the specified parameters.

## Project Structure

The project is structured as follows:

- `processor.py`: The main CPU simulation script.
- `parser.py`: Provides functions for parsing input code and configuration files.
- `instruction.py`: Defines classes for CPU instructions.
- `rf.py`: Implements the register file.
- `pipelined_component.py`: Contains classes for various CPU components like the decoder, execution units, and reorder buffer.
- `scoreboard.py`: Manages dependencies and tracks readiness of registers.
- `branch_unit.py`: Implements branch prediction functionality.
- `config.json`: Sample configuration file for CPU parameters.
- `input_code.txt`: Sample input code file.
- `README.md`: You are reading it now.


```

Replace `"https://github.com/yourusername/OoO-Simulator.git"` with the actual URL of your GitHub repository. This README provides an overview, features, usage instructions, project structure, and guidance for contributing to your project, along with licensing information.

Remember to customize the README with specific details about your project and update the installation and usage instructions based on any project-specific requirements or dependencies.
