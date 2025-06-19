<div align="center">
  <a href="https://github.com/ConvoAI-Capstone-SpSu2025/currensee">
    <img src="images/currensee.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">CurrenSee</h3>

  <p align="center">
    Conversational AI interface to aid in client preparation using data from Microsoft 365, google products, earnings reports, and more.
    <br />
    <a href="https://github.com/ConvoAI-Capstone-SpSu2025/currensee">View Repository</a>
    &middot;
    <a href="https://github.com/ConvoAI-Capstone-SpSu2025/currensee/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    &middot;
    <a href="https://github.com/ConvoAI-Capstone-SpSu2025/currensee/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>

## Getting Started

To get a local copy up and running, follow these simple steps.

### Local Environment Configuration

Below are the recommended operating-system-specific instructions for:
* Installing & configuring git
* Setting up Visual Studio Code

**NOTE**: While it is not necessary that you use Visual Studio Code, it is recommended, as it contains useful extensions and add-ins that will assist with development, especially those related to Microsoft tools.

#### Install Necessary Tools

**NOTE**: It is assumed that you have Python 3.x installed (not Python 13.0 as previously stated; Python 13.0 does not exist as of this writing). If you need assistance with installing Python, please contact one of the administrators of this repository.

1. Install [VSCode](https://code.visualstudio.com/download)
2. Install [git](https://git-scm.com/downloads)
   * If you have a Mac, git may already be installed on your system. To test this, run `git --version` in your terminal.
   * If you are using a Windows 11 machine, you should now open a Git Bash terminal for the remaining steps.
3. Install [poetry](https://python-poetry.org/docs/#installation)
   * IMPORTANT: You may need to add your `~/.local/bin` folder to your path if you are on a Windows or Mac machine. For Mac, see [this article](https://medium.com/@B-Treftz/macos-adding-a-directory-to-your-path-fe7f19edd2f7).
   * Run `poetry --version` to validate that the installation was successful.

#### Configure VSCode

If you decide to use VSCode, these extensions will make your experience much easier.

1. Enable `git` in the settings.
   * Follow the instructions in [this YouTube video](https://youtu.be/3Tsaxxv9sls?si=VsSBTenx6jm_K_tY&t=153)
2. (Windows ONLY) Configure `git bash` as your default terminal.
   * Now that you have git/git bash installed, you should be able to open a git bash terminal in VSCode. Follow the instructions [here](https://csweb.wooster.edu/mionescu/cs232/guides/vs-code-default-terminal/#:~:text=Open%20Visual%20Studio%20Code,the%20menu%20that%20pops%20up.) to configure git bash as your default terminal.
   * Mac users will likely prefer to use Terminal or another shell.

#### Configure Git

1. Add your SSH keys to your GitHub account.
   * Follow the instructions [here](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account).
2. Configure your git username and email:
   ```bash
   git config user.name "<your-username>"
   git config user.email "<your-github-email>"
   ```
3. Clone the repository:
   ```bash
   git clone git@github.com:ConvoAI-Capstone-SpSu2025/currensee.git
   ```

#### Configure the Python Environment

1. Create the environment from the existing poetry specs in the repository.
   ```bash
   poetry config virtualenvs.in-project true
   poetry env use 3.11.12
   poetry env activate 
   # copy and execute the command that is printed out
   poetry install
   ```
   This will create and activate a virtual environment and install all dependencies.

2. If you wish to use another environment manager (e.g., conda, pyenv), ensure you install all dependencies listed in [pyproject.toml](pyproject.toml).

3. Initialize pre-commit

    Pre-commit refers to a framework that manages and maintains scripts, called pre-commit hooks, that run automatically before a code commit is finalized in a version control system like Git. 
    Think of it like a quality control checkpoint before your code changes are officially recorded in the project's history.

    Run the command below to ensure that pre-commit runs each time you commit files.

    ```bash
    pre-commit install
    ```

#### Environment Variables

- Copy `.env.example` to `.env` and fill in any required secrets or configuration values.
- The `credentials/` directory contains service account files (e.g., for Google Cloud). Ensure you have the correct credentials for your environment.

## Usage

### Repository Structure

This repository follows a structure inspired by the [Cookiecutter Data Science](https://cookiecutter-data-science.drivendata.org/) standard.

```
├── LICENSE
├── README.md
├── pyproject.toml         <- Project configuration and dependencies (used by poetry)
├── poetry.lock            <- Poetry lock file for reproducible installs
├── .env.example           <- Template environment variable files
├── currensee/             <- Main source code package
│   ├── __init__.py
│   ├── agents/            <- Agent-related modules
│   ├── core/              <- Core logic and utilities
│   ├── schema/            <- Data schemas and validation
│   ├── utils/             <- Utility functions
│   ├── workflows/         <- Workflow definitions
│   └── README.md
├── data/                  <- Data storage (external, interim, processed, raw, etc.)
├── images/                <- Project images and logos
├── notebooks/             <- Jupyter notebooks for exploration and workflows
├── utils/                 <- Additional utility scripts unrelated to agent operation
├── .gitignore
```

**Key files and directories:**
- [`pyproject.toml`](pyproject.toml): Poetry configuration and dependencies.
- [`currensee/`](currensee/): Main Python package with submodules for agents, core logic, schemas, utilities, and workflows.
- [`data/`](data/): Data storage for CRM and generated reports.
- [`notebooks/`](notebooks/): Jupyter notebooks for data exploration and workflow prototyping.

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for more information.

## Contact

Project Link: [https://github.com/ConvoAI-Capstone-SpSu2025/currensee](https://github.com/ConvoAI-Capstone-SpSu2025/currensee)

## Acknowledgments

- [Cookiecutter Data Science](https://cookiecutter-data-science.drivendata.org/)
- [VSCode](https://code.visualstudio.com/)
