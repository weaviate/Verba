---
name: Verba Issue Template
about: Encountering errors or issues with Verba
title: "Latest Python not supported"
labels: "version"
assignees: ""
---

## Description

<!-- A clear and concise description of what the issue is. Please include any error messages and logs. If possible, also include your configuration. -->

Using Python 3.13.0 with Macbook M1. Cannot install Verba via pip install goldenverba: 

  error: command '/usr/bin/clang' failed with exit code 1
                  [end of output]
      
              note: This error originates from a subprocess, and is likely not a problem with pip.
              ERROR: Failed building wheel for blis
            Failed to build blis
            ERROR: ERROR: Failed to build installable wheels for some pyproject.toml based projects (blis)
            [end of output]
      
        note: This error originates from a subprocess, and is likely not a problem with pip.
      error: subprocess-exited-with-error
      
      × pip subprocess to install build dependencies did not run successfully.
      │ exit code: 1
      ╰─> See above for output.
      
      note: This error originates from a subprocess, and is likely not a problem with pip.
      [end of output]
  
  note: This error originates from a subprocess, and is likely not a problem with pip.
error: subprocess-exited-with-error

× pip subprocess to install build dependencies did not run successfully.
│ exit code: 1
╰─> See above for output.

note: This error originates from a subprocess, and is likely not a problem with pip.

## Installation

<!-- Please specify how you installed Verba. Please always make sure to install Verba in a clean python environment and have at least 3.10.0 installed -->

- [X] pip install goldenverba
- [ ] pip install from source
- [ ] Docker installation

If you installed via pip, please specify the version: pip 22.3

## Weaviate Deployment

<!-- Please specify the Weaviate deployment you are using. -->

- [X] Local Deployment
- [ ] Docker Deployment
- [ ] Cloud Deployment

## Configuration

<!-- If you can, please specify the what components you are using. -->

Reader:
Chunker:
Embedder:
Retriever:
Generator:

## Steps to Reproduce

<!-- If this is a bug, please provide detailed steps on how to reproduce the issue. If this is a feature, please describe what you want to be added or changed. --> 

1. Install Python 3.13.0
2. Create and run venv
3. pip install goldenverba

## Additional context

<!-- Add any other context about the problem here. -->

fixed with python3.11 -m venv venv

