# Image QA Agent

A professional product image quality assessment tool that uses Claude AI to compare raw product images against AI-generated versions and provide detailed fidelity analysis.

Watch Demo [here](https://drive.google.com/file/d/164dKVIdJmO3pDiJArObP417zgcnWtGHM/view)

## Features

- **Visual Fidelity Analysis**: Compare raw product images with AI-generated versions
- **Comprehensive Scoring**: Evaluate images across 5 key dimensions:
  - Color Accuracy
  - Shape & Form
  - Texture & Material
  - Branding & Details
  - Overall Realism
- **Issue Detection**: Automatically identify and locate problems with bounding boxes
- **Visual Annotations**: Generate annotated images highlighting identified issues
- **Improvement Suggestions**: Get actionable recommendations for better AI image generation
- **Web Interface**: Easy-to-use Gradio web application

## Installation

### Prerequisites

- Python 3.12 or higher
- Anthropic API key (for Claude AI)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd image-qa-agent
```

2. Create a virtual environment:
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your Anthropic API key:
Create a `.env` file in the project root:
```
ANTHROPIC_API_KEY=your_api_key_here
```

## Usage

### Web Interface

Run the Gradio web application:

```bash
python app.py
```

Open your browser to the provided URL (typically http://localhost:7860) and:

1. Upload a raw product image (ground truth)
2. Upload an AI-generated version of the same product
3. Click "Analyze Images"
4. View the results including:
   - Overall match percentage
   - Individual dimension scores
   - Annotated image with highlighted issues
   - List of identified problems
   - Suggested improvements

### Command Line

You can also check available Claude models:

```bash
python check_claude_models.py
```

## How It Works

The Image QA Agent uses Anthropic's Claude vision models to perform sophisticated image comparison:

1. **Image Encoding**: Both images are encoded and sent to Claude
2. **Structured Analysis**: Claude analyzes the images using a specialized prompt that focuses on product fidelity
3. **Scoring**: Five key aspects are scored from 0-100%
4. **Issue Detection**: Problems are identified with precise bounding box coordinates
5. **Annotation**: Issues are visually marked on the AI-generated image
6. **Reporting**: Comprehensive feedback is provided through the web interface

## Scoring Criteria

The agent evaluates images based on:

- **Color Accuracy**: How well colors match the original
- **Shape & Form**: Product proportions and geometry
- **Texture & Material**: Surface qualities and materials
- **Branding & Details**: Logos, text, and fine details
- **Overall Realism**: General photorealism quality

## Project Structure

```
image-qa-agent/
├── app.py                 # Main Gradio web application
├── check_claude_models.py # Utility to check available Claude models
├── pyproject.toml         # Project configuration
├── README.md             # This file
├── agent/
│   ├── __init__.py
│   ├── annotator.py      # Image annotation with bounding boxes
│   └── scorer.py         # Claude AI analysis and scoring
├── utils/
│   ├── __init__.py
│   └── image_utils.py    # Image loading and encoding utilities
└── images_test/          # Test images directory
```

## Dependencies

- `anthropic`: Claude AI API client
- `gradio`: Web interface framework
- `opencv-python-headless`: Image processing
- `pandas`: Data handling
- `pillow`: Image manipulation
- `python-dotenv`: Environment variable management

## API Key Setup

You need an Anthropic API key to use this tool. Get one from [Anthropic's website](https://console.anthropic.com/) and add it to your `.env` file.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues or questions, please open an issue on the GitHub repository.
