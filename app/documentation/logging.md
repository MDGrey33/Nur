
# Logging in the Nur Project

## Quick Start

### Getting Started with Logging

1. **Import the Logger in Your Module**

    ```python
    from app.logging.logger import setup_logger
    ```

2. **Initialize the Logger**

    ```python
    logging = setup_logger()
    ```

3. **Use the Logger**

    Log messages at different severity levels as needed.

    ```python
    logging.info("Handling channel messages")
    logging.error("Error in handling channel messages")
    ```

### Finding Your Log Files

**Location**: `./content/logging/[package_name]/[file_name].log`

**Example Log File Name**: `nur.log`

---

## Detailed Guide

### Introduction to Logging in the Nur Project

The Nur project incorporates an advanced logging system designed to support developers in effectively monitoring and debugging their applications. This system is highly configurable, allowing for detailed logging across different parts of the application.

### Features of the Nur Logging System

- **Automatic Package Name Deduction**: Automatically categorizes logs by the package name.
- **Configurable Log Levels**: Enables control over log verbosity for development or production.
- **Color-Coded Logs**: Enhances log readability through color-coded severity levels.
- **Rotating File Handlers**: Optimizes log file management and disk space.
- **Customizable Log Formatting**: Offers flexibility in log presentation.

### Integrating Logging into Your Module

**Step 1: Import the Logger**

Ensure your module has access to the logging system.

```python
from app.logging.logger import setup_logger
```

**Step 2: Initialize the Logger**

Get a configured logger instance for use in your module.

```python
logger = setup_logger()
```

**Step 3: Logging Practices**

Utilize the logger to record events or errors.

```python
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical issue")
```

### Log File Management

Logs are stored at `./content/logging/[package_name]/[file_name].log`, with `nur.log` being an example of a log file created by the system. The logging system employs rotating file handlers to manage file size and archival.

### Configuration and Best Practices

- **Configuration**: Logging configurations are specified in `configuration.py`, including log file paths.
- **Use Appropriate Log Levels**: Match the severity of the log message to its appropriate level.
- **Include Contextual Information**: Provide enough detail in log messages for effective debugging.
- **Regular Review**: Periodically check log files, especially for critical systems, to preemptively address potential issues.
