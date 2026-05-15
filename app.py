import gradio as gr
import os
from agent.scorer import analyze_images
from agent.annotator import annotate_image


def process_images(raw_image, ai_image):
    """
    Main function that processes both images through the QA pipeline.
    Returns: annotated image, overall score, individual scores, issues, improvements
    """
    # Input validation
    if raw_image is None or ai_image is None:
        return None, "Please upload both images", "", "", ""

    # Run the analysis
    result = analyze_images(raw_image, ai_image)

    # Generate annotated image
    output_path = "annotated_output.jpg"
    issues = result.get("issues") or []
    improvements = result.get("improvements") or []
    scores = result.get("scores") or {}

    annotated_path = annotate_image(ai_image, issues, output_path)

    # Format overall score
    overall_score_text = f"**Overall Match: {result.get('overall_match', 0)}%**"

    # Format individual scores
    scores_text = f"""
### Individual Scores:
- **Color Accuracy:** {scores.get("color_accuracy", 0)}%
- **Shape & Form:** {scores.get("shape_and_form", 0)}%
- **Texture & Material:** {scores.get("texture_and_material", 0)}%
- **Branding & Details:** {scores.get("branding_and_details", 0)}%
- **Overall Realism:** {scores.get("overall_realism", 0)}%
"""

    # Format issues
    issues_text = "### Issues Found:\n"
    for idx, issue in enumerate(issues, 1):
        if isinstance(issue, dict):
            description = issue.get("description", "Issue details unavailable")
            bbox = issue.get("bbox")
            if isinstance(bbox, dict):
                bbox_text = (
                    f" [bbox: x_min={bbox.get('x_min', '?')}, y_min={bbox.get('y_min', '?')}, "
                    f"x_max={bbox.get('x_max', '?')}, y_max={bbox.get('y_max', '?')}]"
                )
            else:
                bbox_text = ""
            issues_text += f"{idx}. {description}{bbox_text}\n"
        else:
            issues_text += f"{idx}. {issue}\n"

    # Format improvements
    improvements_text = "### Suggested Improvements:\n"
    for idx, improvement in enumerate(improvements, 1):
        improvements_text += f"{idx}. {improvement}\n"

    return (
        annotated_path,
        overall_score_text,
        scores_text,
        issues_text,
        improvements_text,
    )


# Create the Gradio interface
with gr.Blocks(title="Image QA Agent") as demo:
    gr.Markdown("# Product Image QA Agent")
    gr.Markdown(
        "Compare raw product images with AI-generated versions to check fidelity."
    )

    # Input section
    with gr.Row():
        raw_input = gr.Image(type="filepath", label="Raw Product Image")
        ai_input = gr.Image(type="filepath", label="AI Generated Image")

    analyze_btn = gr.Button("Analyze Images", variant="primary")

    # Output section
    gr.Markdown("## Analysis Results (Claude-sonet-4.0)")

    with gr.Row():
        annotated_output = gr.Image(label="Annotated AI Image")

    with gr.Row():
        with gr.Column():
            overall_score = gr.Markdown()
            individual_scores = gr.Markdown()

        with gr.Column():
            issues_output = gr.Markdown()
            improvements_output = gr.Markdown()

    # Connect button to function
    analyze_btn.click(
        fn=process_images,
        inputs=[raw_input, ai_input],
        outputs=[
            annotated_output,
            overall_score,
            individual_scores,
            issues_output,
            improvements_output,
        ],
    )


if __name__ == "__main__":
    demo.launch()
