
# Logging in the Nur Project

## Quick Start

### Getting Started with Logging

1. **Import the Logger in Your Module**

    ```python
   from nurai.logger.logger import logging
    ```

2 **Use the Logger**

    Log messages at different severity levels as needed.

    ```python
    logging.info("Handling channel messages")
    logging.error("Error in handling channel messages")
    ```

### Finding Your Log Files

    Log files are stored at `./content/logging/app_log[timestamp].log`. 
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
   from nurai.logger.logger import logging
```

**Step 2: Logging Practices**

Utilize the logger to record events or errors.

```python
logging.debug("Debug message")
logging.info("Info message")
logging.warning("Warning message")
logging.error("Error message")
logging.critical("Critical issue")
```

### Log File Management

Log files are stored at `./content/logging/app_log[timestamp].log`.

### Configuration and Best Practices

- **Configuration**: Logging configurations are specified in `configuration.py`, including log file paths.
- **Use Appropriate Log Levels**: Match the severity of the log message to its appropriate level.
- **Include Contextual Information**: Provide enough detail in log messages for effective debugging.
- **Regular Review**: Periodically check log files, especially for critical systems, to preemptively address potential issues.
