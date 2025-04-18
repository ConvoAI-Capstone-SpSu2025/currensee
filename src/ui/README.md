# CurrenSee Outlook UI Package

## Overview
The `ui` package is part of the **CurrenSee** Outlook add-in project. This add-in is designed to enhance the user's meeting experience by summarizing past email correspondence with meeting attendees, with a focus on providing relevant insights 15 minutes before the scheduled meeting. It supports both Microsoft Outlook and Teams meetings.

## Features
- **Email Summary**: The add-in summarizes past email correspondence with meeting attendees.
- **Pre-Meeting Insights**: Provides a meeting summary 15 minutes before the meeting starts, directly in the Outlook calendar item.
- **Teams and Outlook Integration**: Supports both Outlook meetings and Teams meetings.
- **Custom UI**: The user interface is designed to be intuitive and accessible, ensuring users can easily view past communications and meeting details.

## Prerequisites
To use and develop the CurrenSee Outlook UI package, you will need:

- **Microsoft Outlook** (2016 or later)
- **Node.js** (for building and running the UI package)
- **Microsoft Office Add-in** development tools
- **Outlook Office Add-ins API** enabled

### Development Environment
Make sure to have Python (for setting up virtual environments) and Node.js installed on your machine.

## 1. Install Dependencies
Once you've set up the virtual environment, navigate to the ui package folder and install any necessary dependencies by running:
```bash
npm install
```

## 2. Run the Build Script
Once your dependencies are installed, run the build script defined in your package.json. To do this, execute the following command in your terminal:
```bash
npm build
```

## 3. Running the UI Package
To run the ui package, you can use the following command from the terminal:
```bash
npm start
```

This will launch the Outlook add-in UI in the browser for development or testing. It should automatically load the UI in Outlook when integrated.
