import cv2
import numpy as np
from PIL import Image


def wrap_text(text, max_chars_per_line=50):
    """
    Wraps long text into multiple lines.
    """
    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        if current_length + len(word) + 1 <= max_chars_per_line:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_length = len(word) + 1

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def annotate_image(image_path: str, issues: list, output_path: str) -> str:
    """
    Draws precise bounding boxes on the AI generated image based on Claude's coordinates.
    Issues can be either strings (old format) or dicts with bbox (new format).
    Returns the path to the saved annotated image.
    """
    # Load image with OpenCV
    img = cv2.imread(image_path)

    # Get dimensions
    height, width = img.shape[:2]

    # Calculate sizes
    font_scale = max(0.4, min(width, height) / 1500)
    thickness = max(2, int(min(width, height) / 600))
    padding = int(min(width, height) / 80)
    line_spacing = int(font_scale * 25)

    current_y = 30

    # Define colors for different issues (cycling through)
    colors = [
        (0, 255, 255),  # Yellow
        (255, 0, 255),  # Magenta
        (0, 255, 0),  # Green
        (255, 128, 0),  # Orange
        (128, 0, 255),  # Purple
    ]

    # Draw each issue
    for idx, issue in enumerate(issues):
        # Handle both old format (string) and new format (dict with bbox)
        if isinstance(issue, dict):
            issue_text = issue.get("description", "Unknown issue")
            bbox = issue.get("bbox", None)
        else:
            issue_text = issue
            bbox = None

        # Get color for this issue
        color = colors[idx % len(colors)]

        # Draw bounding box if coordinates are provided
        if bbox and all(k in bbox for k in ["x_min", "y_min", "x_max", "y_max"]):
            # Convert percentage coordinates to pixels
            x_min = int(bbox["x_min"] * width / 100)
            y_min = int(bbox["y_min"] * height / 100)
            x_max = int(bbox["x_max"] * width / 100)
            y_max = int(bbox["y_max"] * height / 100)

            # Ensure coordinates are within image bounds
            x_min = max(0, min(x_min, width - 1))
            y_min = max(0, min(y_min, height - 1))
            x_max = max(0, min(x_max, width))
            y_max = max(0, min(y_max, height))

            # Draw thick bounding box
            cv2.rectangle(img, (x_min, y_min), (x_max, y_max), color, thickness)

            # Draw semi-transparent overlay inside box for emphasis
            overlay = img.copy()
            cv2.rectangle(overlay, (x_min, y_min), (x_max, y_max), color, -1)
            cv2.addWeighted(overlay, 0.15, img, 0.85, 0, img)

            # Add issue number badge near the box
            badge_size = int(min(width, height) / 40)
            badge_x = x_min + badge_size + 5
            badge_y = y_min + badge_size + 5

            # Make sure badge is within image
            if badge_y < height and badge_x < width:
                cv2.circle(
                    img, (badge_x, badge_y), badge_size, (0, 0, 255), -1
                )  # Red fill
                cv2.circle(
                    img, (badge_x, badge_y), badge_size, (255, 255, 255), 2
                )  # White border

                # Add number
                cv2.putText(
                    img,
                    str(idx + 1),
                    (badge_x - badge_size // 3, badge_y + badge_size // 3),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    font_scale * 1.5,
                    (255, 255, 255),
                    max(2, thickness),
                    cv2.LINE_AA,
                )

        # Wrap text into multiple lines
        full_text = f"Issue {idx + 1}: {issue_text}"
        wrapped_lines = wrap_text(full_text, max_chars_per_line=40)

        # Calculate total height needed
        total_text_height = len(wrapped_lines) * line_spacing

        # Find maximum text width
        max_text_width = 0
        for line in wrapped_lines:
            (text_width, text_height), _ = cv2.getTextSize(
                line, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness - 1
            )
            max_text_width = max(max_text_width, text_width)

        # Draw semi-transparent background rectangle for text
        overlay = img.copy()
        cv2.rectangle(
            overlay,
            (10, current_y - padding),
            (
                20 + max_text_width + padding * 2,
                current_y + total_text_height + padding,
            ),
            color,  # Use same color as the bounding box
            -1,
        )
        cv2.addWeighted(overlay, 0.7, img, 0.3, 0, img)

        # Draw white border around text box
        cv2.rectangle(
            img,
            (10, current_y - padding),
            (
                20 + max_text_width + padding * 2,
                current_y + total_text_height + padding,
            ),
            (255, 255, 255),
            2,
        )

        # Draw each wrapped line
        line_y = current_y
        for line in wrapped_lines:
            cv2.putText(
                img,
                line,
                (15 + padding, line_y + int(line_spacing * 0.7)),
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale,
                (255, 255, 255),
                thickness - 1,
                cv2.LINE_AA,
            )
            line_y += line_spacing

        # Move to next issue position
        current_y += total_text_height + padding * 3

    # Convert BGR to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Convert to PIL and save
    pil_image = Image.fromarray(img_rgb)
    pil_image.save(output_path, "JPEG", quality=95)

    return output_path
