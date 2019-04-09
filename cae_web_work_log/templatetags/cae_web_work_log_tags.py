"""
Custom template tags for CAE Web Work Log app.
"""

from django import template


register = template.Library()


@register.simple_tag
def format_description(entry_description):
    """
    Format a log entry.
    """
    lines = entry_description.splitlines(True)
    formatted_description = ''
    prev_line = None

    # Iterate through each line of description.
    for line in lines:
        index = 0
        indentation = 0
        style_css = ''
        line = line.strip()

        # Handling for empty lines.
        if len(line) == 0:
            formatted_description += '<br>'
        else:

            # Handle for lines ending in a colon.
            if line[-1] == ':':
                style_css += ' font-weight: bold;'

            # Handle for bullet points.
            try:
                while line[index] == '*':
                    indentation += 1
                    index += 1
            except IndexError:
                # Prevent errors if line ends in a star.
                pass

            if indentation > 0:
                # Replace with prettier bullet point.
                line = ' &#8226; {0}'.format(line[(index):])

                # Format line indentations.
                style_css += ' padding-left: {0}%;'.format((indentation * 2))

            # Handle if any css styles were created.
            if len(style_css) > 0:
                formatted_line = '<p style="{0}">{1}</p>'.format(style_css, line)
            else:
                formatted_line = '<p>{0}</p>'.format(line)

            # Save current line to full 'formatted_description' object.
            formatted_description += formatted_line

    return formatted_description
