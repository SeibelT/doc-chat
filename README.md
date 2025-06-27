
![](.\Frontend\assets\docchat.png)
This intelligent chatbot is designed to support patients in understanding their medical procedures through clear, accessible explanations based on the official informed consent form. It  ensures that patients are truly informed before giving their consent. By providing answers in real-time and using easy-to-understand language, the chatbot enhances patient confidence, supports compliance, and improves the overall consent process for healthcare providers.
## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Configuration](#configuration)
6. [Contributing](#contributing)
7. [FAQ](#faq)
8. [License](#license)
9. [Acknowledgments](#acknowledgments)
10. [Tips and Tricks](#tips-and-tricks)

---

## Overview

This project is a **LLM**(Large Language Model) based  chatbot  designed to guide patients through the informed consent process before a medical procedure. It ensures that patients receive accurate, comprehensible, and consistent information derived directly from the official informed consent documents — minimizing the risk of hallucinated or incorrect answers.

##  Key Features


**RAG-based** architecture: Combines retrieval from approved informed consent documents with generative responses to ensure factual accuracy and relevance.

**Multi-level language prompts**: Offers three different levels of explanation (basic, intermediate, and detailed) to adapt to each patient’s health literacy.

**Web-based interface**: A user-friendly web application where patients can interact with the chatbot in a conversational format.

**Session history and traceability**: All interactions are stored securely, enabling:
Doctors to review the full question-answer history for compliance and clarification.
Patients to receive a summarized transcript of their session for reference and review.


This tool enhances patient understanding, supports shared decision-making, and streamlines documentation for healthcare providers.

---


## Installation & Usage 

**Prerequisites**:
- Python 3.9+, pip, GPU (for faster inference).

**Steps**:
```bash
# Clone the repository
git clone https://github.com/username/repository-name.git

# Navigate to the directory
cd repository-name

# Create virtual environment with venv 
pip install -m venv .env

# Activate Virtual Environment
pip source ./.env/bin/activate



# Run code (with activated virtual environment)
python ./run_chatbot.py
```
### Example Output
Provide a brief description or screenshots of expected outputs (if applicable).

## Citation

## Acknowledgments # FIXME !!!!
Mention contributors, libraries, and resources used in the project.

## License
This project is licensed under the GNU General Public License v3.0 - see the [LICENSE.md](LICENSE.md) file for details.
