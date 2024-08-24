# Benchmark Helper
![Python](https://img.shields.io/badge/language-Python-blue)
![JavaScript](https://img.shields.io/badge/Language-JavaScript-yellow)
![CSS](https://img.shields.io/badge/Language-CSS-blue)
![HTML](https://img.shields.io/badge/Language-HTML-orange)
![License](https://img.shields.io/badge/License-Apache%202.0-blue)
![Build Status](https://img.shields.io/github/actions/workflow/status/yetanotheruservasya/benchmark_helper/app.yml?branch=main)
![Contributors](https://img.shields.io/github/contributors/yetanotheruservasya/benchmark_helper)

## Описание

Benchmark Helper — is a project designed to analyze and evaluate operational performance. This project includes Python scripts and web resources for data visualization and management, which allows you to effectively compare and analyze various operational indicators.
Main concept was described on [LinkedIn Article](https://www.linkedin.com/pulse/personal-assistant-coo-pmo-project-description-vasiliy-fadeev-ahfle/?trackingId=FsScFlp6ThGZHjvjtrf0lA%3D%3D)

## Project structure

Folowwing components are included in the project:

- **`app.py`** — the main file to start the server.
- **`requirements.txt`** — the file listing the dependencies required for the project. Use it to install all necessary packages..
- **`prompts/`** — directory with files used for generating prompts.
    - **`prompt_generator.py`** — script for generating prompts that assists in task automation.
- **`static/`** — folder with static files such as CSS styles and JavaScript scripts.
  - **`css/`** — folder with CSS files.
    - **`styles.css`** — main CSS file containing styles for the web interface.
- **`templates/`** — folder with HTML templates for web pages.
    - **`index.html`** — main HTML template used for displaying the main page of the web interface.

## Install

To install and run the project, follow these steps:

1. Clone the repository:

    ```bash
    git clone "https://github.com/yetanotheruservasya/benchmark_helper.git"
    ```

2. Navigate to the project directory:

    ```bash
    cd path/to/benchmark_helper
    ```

3. Install the dependencies listed in `requirements.txt`:

    ```bash
    pip install -r requirements.txt
    ```

## Running

To start the application, use the following command:

```bash
python app.py
```

This will start the server, which will be available by default at [http://localhost:5000](http://localhost:5000).

## Usage

After starting the application, open your web browser and go to [http://localhost:5000](http://localhost:5000). You will see an interface that allows you to analyze and evaluate operational metrics.


## License

This project is licensed under the MIT License. See the `LICENSE` file for details.


## Contact

If you have any questions or suggestions, please contact me on [LinkedIn](https://www.linkedin.com/in/vasiliy-fadeev-b2b-product-management-iot-mes/) or open an issue in the repository.
