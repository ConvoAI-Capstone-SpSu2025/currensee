<a id="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/ConvoAI-Capstone-SpSu2025/currensee">
    <img src="images/currensee.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">CurrenSee</h3>

  <p align="center">
    Conversational AI interface to aid in client preparation using data from Microsoft 365, google products, earnings reports, and more.
    <br />
    <a href="https://github.com/ConvoAI-Capstone-SpSu2025/currensee"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/ConvoAI-Capstone-SpSu2025/currensee">View Demo</a>
    &middot;
    <a href="https://github.com/ConvoAI-Capstone-SpSu2025/currensee/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    &middot;
    <a href="https://github.com/ConvoAI-Capstone-SpSu2025/currensee/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple steps.

### Local Environment Configuration

Below are the recommended operating-system-specific instructions for:
* Installing & configuring git
* Setting up visual studio code

**NOTE**: While it is not necessary that you use visual studio code, it is recommended, as it contains useful extensions and add-ins that will assist with development, especially those related to microsoft tools.

#### Install Necessary Tools

**NOTE**: It is assumed that you have python 13.0 installed. If you need assistance with installing python, please contact one of the administrators of this repository.

1. Install [VSCode](https://code.visualstudio.com/download) 
2. Install [git](https://git-scm.com/downloads)
* If you have a mac, git may already be installed on your system. To test this, run `git --version` in xcode.

*If you are using a Windows 11 machine, you should now open a git bash terminal (search in the search bar) for the remaining steps.*

3. Install [poetry](https://python-poetry.org/docs/#installation)
* IMPORTANT: You may need to add your `~/.local/bin` folder to your path if you are on a windows machine. The install of `pipx` should prompt you to do this. In order to do this, you will need to run the following command in your git bash terminal: `export PATH="$PATH:/path/to/your/bin"`.
* For MAC I had to follow the instructions in this article to add the '/Users/"myusername"/.local/bin' to my path https://medium.com/@B-Treftz/macos-adding-a-directory-to-your-path-fe7f19edd2f7
* Run `poetry --version` to validate that the installation was successful.


#### Configure VSCode
If you decide to use VSCode, these extensions will make your experience much easier.

1. Enable `git` in the settings.
* Follow the instructions in [this youtube video](https://youtu.be/3Tsaxxv9sls?si=VsSBTenx6jm_K_tY&t=153)

2. (Windows ONLY) Configure `git bash` as your default terminal.
* Now that you have git/git bash installed, you should be able to open a git bash terminal in vscode. Follow the instructions [here](https://csweb.wooster.edu/mionescu/cs232/guides/vs-code-default-terminal/#:~:text=Open%20Visual%20Studio%20Code,the%20menu%20that%20pops%20up.) to configure git bash as you default terminal.
* Mac users will likely prefer to use `xcode` or another terminal.

#### Configure Git

1. Add your ssh keys to your git account. 
* Follow the instructions [here](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account).

2. Configure your git username and email
```bash
git config user.name "<your-username>"
git config user.email "<your-github-email>"
```

3. Clone the repostiory
```bash
git clone git@github.com:ConvoAI-Capstone-SpSu2025/currensee.git
```

#### Configure the Python Environment

1. Create the environment from the existing poetry specs in the repository.
Below are instructions for creating an environment via poetry, but you can
also use the environment of your choice (conda, pyenv, etc.) .

```bash
poetry env activate 
# copy the command and call it to activate the environment
poetry install # install the packages into the environment
```


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

### Repository Structure

For this repository, we leverage the [Cookiecutter Data Science](https://cookiecutter-data-science.drivendata.org/) standard to define a structure
that optimizes code quality, prioritizing correctness and reproucibility. Below is an outline of the repository and the contents you should expect
to find in each folder/file.

```
├── LICENSE            <- Open-source license 
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data (if we do not have a DB, which we should...)
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default mkdocs project; see www.mkdocs.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for 
│                         {{ cookiecutter.module_name }} and configuration for tools like black
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
|
├── app                <- Contains the app-specific files (e.g API router, streamlit/UI files, teams/outlook interaction, etc.)
|
├── src
    | 
    └── currensee  <- Source code for the project containing modeling/workflows files.
        |
        ├── data_loading            <- Files necessary to perform data ingestion
        |
        ├── evaluation              <- Defines files for the evaluation framework (if necessary)
        |
        ├── modeling                <- Files necessary for model development
        |
        ├── serve                   <- Files that define project-wide schemas and modules necessary for communicating model results with the UI
        |
        ├── utils                   <- Utility files (e.g. workflow_utils.py, db_utils.py, etc.)
|
├── tests                           <- Test files to evaluate model performance

```

<p align="right">(<a href="#readme-top">back to top</a>)</p>





<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

* Lily Campbell - lilycampbell@uchicago.edu
* Xiaojing Fang - xjfang@uchicago.edu
* Gretchen Forbush - forbug@uchicago.edu
* Stepan Ochodek - sochodek@uchicago.edu
* Alen Pavlovic - apavlovic@uchicago.edu


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

Use this space to list resources you find helpful and would like to give credit to. 


<p align="right">(<a href="#readme-top">back to top</a>)</p>



