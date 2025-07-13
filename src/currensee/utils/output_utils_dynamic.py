import datetime
import os
import re
import webbrowser
from typing import Any, Dict, List, Optional, TypedDict

import markdown
import matplotlib.pyplot as plt
import weasyprint
from weasyprint import HTML

from currensee.agents.tools.finance_tools import generate_macro_table
from currensee.utils.get_logo_utils import get_logo


def convert_markdown_links_to_html(text: str) -> str:
    """
    Converts markdown-style links like [Source 1](https://example.com)
    into <a href="https://example.com">Source 1</a>
    """
    return re.sub(
        r"\[([^\]]+)\]\((https?://[^\)]+)\)",
        r'<a class="source-link" href="\2" target="_blank" rel="noopener noreferrer">\1</a>',
        text,
    )


def format_news_summary_to_html(news_summary, title):
    html = f"<h2>{title}</h2>"
    for article in news_summary:
        html += "<div style='margin-bottom:20px;'>"
        html += f"<h4>{article.get('title', 'No Title')}</h4>"
        html += f"<p><strong>Date:</strong> {article.get('date', 'No Date')}</p>"
        html += (
            f"<p><strong>Snippet:</strong> {article.get('snippet', 'No Snippet')}</p>"
        )
        html += f"<p><strong>Source:</strong> {article.get('link', '').split('/')[2] if article.get('link') else 'No Source'}</p>"
        html += (
            f"<p><a href='{article.get('link', '')}' target='_blank'>Read more</a></p>"
        )
        html += "</div>"
    return html


# Prepare Holding Sources section
def format_holdings_to_html(sources, title):
    sources_html = f"<div class='sources-section'><h2>{title}</h2>"

    if not sources:
        sources_html += "<p>No results found.</p></div>"
        return sources_html

    for holding_name, sources_list in sources.items():
        sources_html += f"<details class='article'>"
        sources_html += f"<summary style='cursor:pointer; color:#2980B9; font-size:12px;'>{holding_name}</summary>"

        visible = sources_list[:3]
        hidden = sources_list[3:]

        # Show first 3 articles always inside details
        for details_dict in visible:
            sources_html += render_article_html(details_dict)

        if hidden:
            sources_html += """
            <details>
                <summary style='cursor:pointer; color:#2980B9; font-size:12px;'>See All</summary>
            """
            for details_dict in hidden:
                sources_html += render_article_html(details_dict)
            sources_html += "</details>"

        sources_html += "</details>"

    sources_html += "</div>"
    return sources_html


# Prepare Sources section
def format_sources_to_html(sources, title):
    sources_html = f"<div class='sources-section' id='resources'><h2>{title}</h2>"

    if isinstance(sources, str):
        sources_html += f"<p>{sources}</p></div>"
        return sources_html

    if not sources:
        sources_html += "<p>No results found.</p></div>"
        return sources_html

    visible_articles = sources[:3]
    hidden_articles = sources[3:]

    for article in visible_articles:
        if isinstance(article, dict):
            sources_html += render_article_html(article)

    if hidden_articles:
        sources_html += """
        <details>
            <summary style='cursor:pointer; color:#2980B9; font-size:12px;'>See All</summary>
        """
        for article in hidden_articles:
            if isinstance(article, dict):
                sources_html += render_article_html(article)
        sources_html += "</details>"

    sources_html += "</div>"
    return sources_html


def format_paragraph_summary_to_html(summary: str) -> str:
    if not summary or not summary.strip():
        return """
        <div class="box-content">
            <p>No summary available.</p>
        </div>
        """

    # Pattern for markdown-style headers
    section_pattern = r"\*\*(\d+\.\s+[^*]+?)\*\*"
    parts = re.split(section_pattern, summary)

    if len(parts) <= 1:
        return f"""
        <div class="box-content">
            <p>{markdown.markdown(summary)}</p>
        </div>
        """

    # Otherwise, format as sections
    html_sections = []
    for i in range(1, len(parts), 2):
        header = parts[i].strip()
        body = parts[i + 1].strip() if i + 1 < len(parts) else ""
        html_sections.append(f"<h2>{header}</h2>\n{markdown.markdown(body)}")

    full_body = "\n".join(html_sections)
    return f"<div class='box-content'>{full_body}</div>"


def thumbs_buttons(section_id):
    return f"""
    <div style="
        position: absolute;
        top: 8px;
        right: 8px;
        cursor: pointer;
        display: flex;
        gap: 8px;
        ">
        <svg onclick="toggleThumb(this, '{section_id}', true)" title="Thumbs Up"
             xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16"
             fill="#2980B9" style="user-select:none;">
            <path d="M2 21h4V9H2v12zM23 10c0-1.1-0.9-2-2-2h-6.31l0.95-4.57
                     0.03-0.32c0-0.41-0.17-0.79-0.44-1.06L14.17 2 7.59 8.59
                     C7.22 8.95 7 9.45 7 10v9c0 1.1 0.9 2 2 2h7c0.83 0 1.54-0.5
                     1.84-1.22l3.02-7.05c0.09-0.23 0.14-0.47 0.14-0.73v-1z"/>
        </svg>

        <svg onclick="toggleThumb(this, '{section_id}', false)" title="Thumbs Down"
             xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16"
             fill="#2980B9" style="user-select:none;">
            <path d="M22 3h-4v12h4V3zM2 14c0 1.1 0.9 2 2 2h6.31l-0.95 4.57
                     -0.03 0.32c0 0.41 0.17 0.79 0.44 1.06L9.83 22 16.41 15.41
                     C16.78 15.05 17 14.55 17 14v-9c0-1.1-0.9-2-2-2H8c-0.83 0-1.54 0.5
                     -1.84 1.22L3.14 12.27C3.05 12.5 3 12.74 3 13v1z"/>
        </svg>
    </div>
    """



def render_article_html(article):
    title = article.get("title", "No Title")
    snippet = article.get("snippet", "No Snippet")
    date = article.get("date", "No Date")
    link = article.get("link", "")
    source = link.split("/")[2] if link and len(link.split("/")) > 2 else "No Source"

    return f"""
    <div class='article'>
        <h4>{title}</h4>
        <p><strong>Snippet:</strong> {snippet}</p>
        <p><strong>Date:</strong> {date}</p>
        <p><strong>Source:</strong> {source}</p>
        <p><a href="{link}" target="_blank">Read more</a></p>
    </div>
    """


def generate_report(result):

    #Meeting info section
    meeting_title = result.get("meeting_description", "") + " : Briefing Document"
    client_company = result.get("client_company", "")
    client_name = result.get("client_name", "")
    meeting_time = result.get("meeting_timestamp", "")
    last_meeting_time = result.get("last_meeting_timestamp", "")

    #Summary Section
    email_summary = result.get("email_summary", "")
    recent_email_summary = result.get("recent_email_summary", "")
    recent_client_questions = result.get("recent_client_questions", "")

    #Financial Section
    holdings_summary = result.get("fin_hold_summary_sourced", "")
    news_summary = result.get("client_news_summary_sourced", "")
    client_holdings_sources = result.get("client_holdings_sources", list())
    client_industry_sources = result.get("client_industry_sources", list())
    macro_news_sources = result.get("macro_news_sources", list())
    client_holdings = result.get("client_holdings", "")
    client_holdings_list = [str(h).strip() for h in client_holdings if str(h).strip()]
    logo_str = get_logo()

    
    # Format bullet point
    # Format recent email summary as <ul>
    numbered_line_re = re.compile(r"^\d+\.\s+")
    strip_number_re = re.compile(r"^\d+\.\s*")


    # Format recent email summary into unordered list
    if recent_email_summary:
        email_lines = recent_email_summary.strip().split("\n")
        recent_email_summary = (
            "<ul>"
            + "".join(
                f"<li>{line_stripped.strip('•-* ').strip()}</li>"
                for line in email_lines
                if (line_stripped := line.strip()).startswith(("•", "-", "*"))
            )
            + "</ul>"
        )
    
    # Format recent client questions
    if recent_client_questions:
        question_lines = recent_client_questions.strip().split("\n")
        recent_client_questions = (
            "<ul>"
            + "".join(
                f"<li>{strip_number_re.sub('', line).strip()}</li>"
                for line in question_lines
                if strip_number_re.match(line.strip())
            )
            + "</ul>"
        )

    
    # Title block with logos
    document_title_html = f"""
    <div class="header-container">
        {logo_str}
        <h1>{meeting_title}</h1>
    </div>
    """

    # Meeting info block with emojis
    client_holdings_html = "".join(
        f'<span class="client-holding-pill">💼{holding}</span>'
        for holding in client_holdings_list
    )
    meeting_info_html = f"""
    <div class="box-content" style="position: relative;">
        <table class="meeting-info-table">
            <tr>
                <td>Client Company:</td>
                <td>{client_company}</td>
            </tr>
            <tr>
                <td>Client Name:</td>
                <td>{client_name}</td>
            </tr>
            <tr>
                <td>Meeting Time:</td>
                <td>{meeting_time}</td>
            </tr>
            <tr>
            <tr>
                <td>Last Meeting Time:</td>
                <td>{last_meeting_time}</td>
            </tr>
            <tr>
                <td>Client Holdings:</td>
                <td>
                    <div class="client-holdings-container">
                        {client_holdings_html}
                    </div>
                </td>
            </tr>
        </table>

    </div>
    """

    # Macro Table section
    macro_news_df = generate_macro_table()
    financial_snapshot_html = "<table class='financial-snapshot'>"
    financial_snapshot_html += """
    <thead>
        <tr>
            <th>Indicator</th>
            <th>Level</th>
            <th>1-Month Change (%)</th>
            <th>3-Month Change (%)</th>
            <th>6-Month Change (%)</th>
            <th>1-Year Change (%)</th>
            <th>2-Year Change (%)</th>
        </tr>
    </thead>
    <tbody>
    """

    for _, row in macro_news_df.iterrows():
        financial_snapshot_html += f"""
        <tr>
            <td>{row['Indicator']}</td>
            <td>{row['Level']}</td>
            <td>{row['1-Month Change (%)']}</td>
            <td>{row['3-Month Change (%)']}</td>
            <td>{row['6-Month Change (%)']}</td>
            <td>{row['1-Year Change (%)']}</td>
            <td>{row['2-Year Change (%)']}</td>
        </tr>
        """

    financial_snapshot_html += "</tbody></table>"

    # News Resource Section
    html_client_industry_sources = format_sources_to_html(
        client_industry_sources, "Client Industry News"
    )
    html_client_holdings_sources = format_holdings_to_html(
        client_holdings_sources, "Client Holdings News"
    )
    html_macro_news_sources = format_sources_to_html(
        macro_news_sources, "Macro Economic News"
    )

    resources_html = f"""
    <div id="resources-content" class="box-content">
        {html_client_industry_sources}
        {html_client_holdings_sources}
        {html_macro_news_sources}
    </div>
    """


    # Toggle boxes for "Email Summary" section
    email_section_full = f"""
    <div class="box-main box-content" style="margin-top: 8px;">
        <div style="position: relative; margin-bottom: 12px;">
            <div>{email_summary}</div>
        </div>
        <div class="box-main box-content" style="margin-top: 12px;">
            <button onclick="toggleBox('recent-email-box')">Recent Email</button>
            <button onclick="toggleBox('client-questions-box')">Client Questions</button>
            <div id='recent-email-box' class='toggle-box' style='display:none;'>{recent_email_summary}</div>
            <div id='client-questions-box' class='toggle-box' style='display:none;'>{recent_client_questions}</div>
        </div>
    
        <div class="feedback-section" style="margin-top: 12px;">
            <div class="feedback-buttons" style="display: flex; justify-content: flex-end; gap: 6px;">
                <button onclick="handleFeedback(this, 'more')">I want to see more of this</button>
                <button onclick="handleFeedback(this, 'less')">I do not want to see this</button>
            </div>
            <div class="feedback-message" style="display:none; color: green; font-size: 0.9em; margin-top: 5px;">
                Got it! We will remember it next time
            </div>
        </div>
    </div>
    """

    # Toggle boxes for "Financial News" section
    financial_section_full = f"""
    <div class="box-main box-content" style="margin-bottom: 8px;">
        <div style="position: relative; margin-bottom: 12px;">
            <div>{holdings_summary}</div>
        </div>
        <div>            
            <button onclick="toggleBox('macro-snap')">Macro-Economic Snapshot</button>
            <button onclick="toggleBox('resources')">Resources</button>
        </div>
        <div style="margin-top: 12px;">
            <div id='macro-snap' class='toggle-box' style='display:none;'>{financial_snapshot_html}</div>
            <div id='resources' class='toggle-box' style='display:none;'> {resources_html}</div>
        </div>
                <div class="feedback-section" style="margin-top: 12px;">
            <div class="feedback-buttons" style="display: flex; justify-content: flex-end; gap: 6px;">
                <button onclick="handleFeedback(this, 'more')">I want to see more of this</button>
                <button onclick="handleFeedback(this, 'less')">I do not want to see this</button>
            </div>
            <div class="feedback-message" style="display:none; color: green; font-size: 0.9em; margin-top: 5px;">
                Got it! We will remember it next time
            </div>
        </div>
    </div>
    """


    # Check if there's meaningful email summary content
    email_content_exists = any([
        email_summary.strip(),
        recent_email_summary.strip(),
        recent_client_questions.strip()
    ])
    
    # Check if there's meaningful financial summary content
    financial_content_exists = any([
        holdings_summary.strip(),
        news_summary.strip(),
        client_holdings_sources,
        client_industry_sources,
        macro_news_sources
    ])
    
    # Conditionally showing summary sections only if there's meaningful content
    
    email_summary_section = f"""
    <div id="email-summary" class="box-section {'hidden-section' if not email_content_exists else ''}">
        <h2>Email Summary</h2>
        {email_section_full}
    </div>
    """
    
    financial_news_section = f"""
    <div id="financial-summary" class="box-section {'hidden-section' if not financial_content_exists else ''}">
        <h2>Financial News Summary</h2>
        {financial_section_full}
    </div>
    """

    
    # Full HTML document
    full_html = f"""
    <html>
    <head>
        <meta charset='UTF-8'>
        <title>{meeting_title}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 15px;
                color: #333;
                max-width: 800px;
                margin: 20px auto; /* less vertical margin */
                line-height: 1.3; /* tighter line spacing */
            }}
            p, ul, ol, li, div {{
                margin: 0 0 8px 0; /* small bottom margin only */
                line-height: 1.3;
                padding: 0;
            }}
            h1 {{
                text-align: center;
                color: #2C3E50;
                font-size: 18px;
                border-bottom: 3px solid #2980B9;
                padding-bottom: 10px;
                margin-bottom: 10px;
            }}
            h2 {{
                color: #2980B9;
                font-size: 16px;
                margin-top: 14px;
                border-bottom: 2px solid #BDC3C7;
                padding-bottom: 5px;
            }}
            h3 {{
                color: #2980B9;
                font-size: 10px;
                margin-top: 12px;
                margin-bottom: 4px;
            }}
            .box-content {{
                margin-top: 20px;
                padding: 8px 20px;
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
            }}
            ul {{
                padding-left: 20px;
            }}
            li {{
                margin-bottom: 6px;
            }}
            button {{
                padding: 6px 12px;
                background-color: #2980B9;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }}
            button:hover {{
                background-color: #1A5276;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            tr:hover {{
                background-color: #f1f1f1;
            }}
            .section-heading {{
                color: #2980B9;
                font-weight: bold;
                font-size: 10px;
                margin-top: 12px;
                margin-bottom: 4px;
            }}
            .sources-section {{
                margin-top: 10px;
                padding: 15px;
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
            }}
            .article {{
                margin-bottom: 12px;
            }}
            .article h4 {{
                color: #2980B9;
                font-size: 10px;
            }}
            .article p {{
                font-size: 10px;
                line-height: 1.2;
            }}
            .header-container {{
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 12px;
                margin-bottom: 10px;
            }}
            .logo {{
                height: 35px;
            }}
            .meeting-info-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
                font-size: 14px;
            }}
            .meeting-info-table td {{
                padding: 2px 4px;
                vertical-align: top;
            }}
            .meeting-info-table td:first-child {{
                width: 130px;
                font-weight: bold;
                color: #2980B9;
                white-space: nowrap;
            }}
            .client-holdings-container {{
                display: flex;
                flex-wrap: wrap;
                gap: 6px;
                margin-top: 4px;
            }}

            .client-holding-pill {{
                background-color: #2980B9;
                color: white;
                padding: 6px 11px;
                border-radius: 12px;
                font-size: 11px;
                white-space: nowrap;
                box-shadow: 0 1px 3px rgba(0,0,0,0.2);
            }}
            .toggle-box {{
                display: none;
                overflow: hidden;
                transition: max-height 0.3s ease-out;
            }}

            .financial-snapshot {{
                width: 100%;
                border-collapse: collapse;
                font-size: 13px;
                margin: 16px 0;
                overflow-x: auto;
                display: block;
                border: 1px solid #ccc;
            }}

            .financial-snapshot thead {{
                background-color: #f0f4f8;
            }}

            .financial-snapshot th,
            .financial-snapshot td {{
                padding: 10px 12px;
                text-align: center;
                border: 1px solid #ddd;
                white-space: nowrap;
            }}

            .financial-snapshot tr:nth-child(even) {{
                background-color: #fafafa;
            }}

            .financial-snapshot tr:hover {{
                background-color: #f1f8ff;
            }}

            @media (max-width: 768px) {{
                .financial-snapshot {{
                    font-size: 12px;
                    display: block;
                    overflow-x: auto;
                }}
            }}

            .feedback-buttons button {{
              border: none;
              color: white;
              padding: 3px 8px;
              margin-right: 6px;
              border-radius: 8px;
              cursor: pointer;
              font-size: 0.7rem;
              font-weight: 500;
              white-space: nowrap;
              box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
              transition: background-color 0.25s ease, box-shadow 0.25s ease;
            }}
            
            .feedback-buttons .btn-more {{
              background-color: #106ebe;  /* Brand blue */
            }}
            
            .feedback-buttons .btn-more:hover {{
              background-color: #005a9e;  /* Darker blue on hover */
              box-shadow: 0 2px 6px rgba(0, 90, 158, 0.3);
            }}
            
            .feedback-buttons .btn-more:active {{
              background-color: #004080;
              box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.2);
            }}
            
            .feedback-buttons .btn-less {{
              background-color: #3b82f6;  
            }}
            
            .feedback-buttons .btn-less:hover {{
              background-color: #2563eb;
              box-shadow: 0 2px 6px rgba(37, 99, 235, 0.4);
            }}
            
            .feedback-buttons .btn-less:active {{
              background-color: #1e40af;
              box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.2);
            }}
            
            .feedback-buttons button:focus {{
              outline: none;
              box-shadow: 0 0 0 2px rgba(16, 110, 190, 0.4); 
            }}

        </style>

        <script>
            function toggleBox(id) {{
                const allBoxes = [
                  'recent-email-box', 'client-questions-box',
                  'macro-snap', 'resources'
                ];
                allBoxes.forEach(boxId => {{
                    document.getElementById(boxId).style.display = (boxId === id) ?
                        (document.getElementById(boxId).style.display === 'none' ? 'block' : 'none') :
                        'none';
                }});
            }}
            function toggleThumb(elem, sectionId, isUp) {{
                const container = elem.parentElement;
                [...container.children].forEach(sibling => sibling.style.color = '#2980B9');

                if(isUp) {{
                    elem.style.color = '#0000FF'; // bright blue
                    document.getElementById(sectionId).style.display = 'block';
                }} else {{
                    document.getElementById(sectionId).style.display = 'none';
                    elem.style.color = '#0000FF';
                }}
            }}


            function handleFeedback(button, type) {{
                const feedbackSection = button.closest('.feedback-section');
                const buttons = feedbackSection.querySelector('.feedback-buttons');
                const message = feedbackSection.querySelector('.feedback-message');
        
                buttons.style.display = 'none';
                message.style.display = 'block';
        
                setTimeout(() => {{
                    message.style.display = 'none';
                }}, 5000);
            }}
            

          function handleFeedback(button, type) {{
            const feedbackSection = button.closest('.feedback-section');
            const buttons = feedbackSection.querySelector('.feedback-buttons');
            const message = feedbackSection.querySelector('.feedback-message');
        
            // Hide buttons only when clicked
            buttons.style.display = 'none';
            message.style.display = 'block';
        
            // Hide message after 5 seconds
            setTimeout(() => {{
              message.style.display = 'none';
            }}, 5000);
          }}

          function openClientHoldingsPage() {{
            window.open('/static/client_holding.html', '_blank');
          }}
          

        </script>

    </head>
    <body>
        <div class="header-container">
            <img src="{logo_str}" alt="Logo" class="logo" />
            <h1>{meeting_title}</h1>
        </div>

            {meeting_info_html}
        
            {email_summary_section}
        
            {financial_news_section}

    </body>
    </html>
    """

    return full_html


def save_html_to_file(html_content: str, filename: str):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)


def convert_html_to_pdf(html_string, output_pdf):
    weasyprint.HTML(string=html_string).write_pdf(
        output_pdf,
        stylesheets=None,
        presentational_hints=True,
        page_size="Letter",
    )


if __name__ == "__main__":
    generate_report(dict())
