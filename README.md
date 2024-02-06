# Asynchronizer

This repository contains a Python decorator and class that allow you to run asynchronous code from a synchronous context. This can be particularly useful when you need to perform IO-bound tasks such as making HTTP requests, reading from or writing to a database, or interacting with the file system, but you are working within a synchronous context.

## Installation

You can install the `asynchronizer` package using pip. Open your terminal and type:

```bash
pip install asynchronizer
```

## Usage

Here are some examples of how you can use the `asynchronizer` package.

### Using the decorator

```python
from asynchronizer import asynchronize

@asynchronize
async def async_function():
    # Your asynchronous code here

async_function()
```

In the above example, `async_function` is an asynchronous function decorated with `@async_to_sync`. This allows it to be called from a synchronous context.

### Using the class

```python
from asynchronizer import Asynchronizer

async def async_function():
    # Your asynchronous code here

asynchronizer = Asynchronizer()
asynchronizer.run(async_function())
```

In this example, an instance of `Asynchronizer` is created. The `run` method is then used to execute `async_function` from a synchronous context.

## Contributing

Contributions are welcome! Please read the [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.