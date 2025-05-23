import datetime
from typing import TypedDict, List, Dict, Any, Optional
import matplotlib.pyplot as plt
import re
import weasyprint
from weasyprint import HTML
import webbrowser
import os
import markdown

from currensee.agents.tools.finance_tools import generate_macro_table
from currensee.utils.get_logo_utils import get_logo



def format_news_summary_to_html(news_summary, title):
    html = f"<h2>{title}</h2>"
    for article in news_summary:
        html += "<div style='margin-bottom:20px;'>"
        html += f"<h4>{article.get('title', 'No Title')}</h4>"
        html += f"<p><strong>Date:</strong> {article.get('date', 'No Date')}</p>"
        html += f"<p><strong>Snippet:</strong> {article.get('snippet', 'No Snippet')}</p>"
        html += f"<p><strong>Source:</strong> {article.get('link', '').split('/')[2] if article.get('link') else 'No Source'}</p>"
        html += f"<p><a href='{article.get('link', '')}' target='_blank'>Read more</a></p>"
        html += "</div>"
    return html

# Prepare Holding Sources section
def format_holdings_to_html(sources, title):
    sources_html = f"<div class='sources-section'><h3>{title}</h3>"

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
    sources_html = f"<div class='sources-section' id='resources'><h3>{title}</h3>"

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



def format_paragraph_summary_to_html(summary: str, title: str, logo_str: str) -> str:
    if not summary:
        return f"""
        <div class="main-header">
            <h1>{title}</h1>
        </div>
        <div class="box-content">
            <p>No summary available.</p>
        </div>
        """
    pattern = r'\*\*(\d+\.\s+[^*]+?)\*\*'
    headers = re.findall(pattern, summary)
    parts = re.split(pattern, summary)
    html_sections = []

    for i in range(1, len(parts), 2):
        header = parts[i].strip()                    
        body = parts[i+1].strip() if i+1 < len(parts) else '' 

        header_html = f"<h2>{header}</h2>"
        body_html = markdown.markdown(body)

        if header.startswith("4. Financial Overview"):
            body_html += """
            <p style="margin-top:10px;text-align: right;">
                <a href="#resources" style="color:#2980B9; font-weight:bold; text-decoration:none;">
                    See Sources
                </a>
            </p>
            """

        html_sections.append(f"{header_html}\n{body_html}")
    full_body = "\n".join(html_sections)
    return f"""
    <div class="header-container">
        <img src="{logo_str}" class="logo" alt="Logo">
        <h1>{title}</h1>
    </div>
    <div class="box-content">
        {full_body}
    </div>
    """

   # return f"""
  #  <div class="main-header">
  #      <h1>{title}</h1>
  #  </div>
  #  <div class="box-content">
  #      {full_body}
  #  </div>
  #  """

def render_article_html(article):
    title = article.get('title', 'No Title')
    snippet = article.get('snippet', 'No Snippet')
    date = article.get('date', 'No Date')
    link = article.get('link', '')
    source = link.split("/")[2] if link else 'No Source'

    return f"""
    <div class='article'>
        <h4>{title}</h4>
        <p><strong>Snippet:</strong> {snippet}</p>
        <p><strong>Date:</strong> {date}</p>
        <p><strong>Source:</strong> {source}</p>
        <p><a href="{link}" target="_blank">Read more</a></p>
    </div>
    """


def generate_long_report(result):
    meeting_title = result.get('meeting_description', '') + ' : Briefing Document'
    client_holdings_sources = result.get('client_holdings_sources', list())
    client_industry_sources = result.get('client_industry_sources', list())
    macro_news_sources = result.get('macro_news_sources', list())
    final_summary = result.get('final_summary', '')
    client_company = result.get('client_company', '')
    logo_str = get_logo()
    # Email/financial news data section
    html_summary = markdown.markdown(final_summary)
    html_summary_split = re.split(r"\n", html_summary)
    html_summary_final = format_paragraph_summary_to_html(final_summary, meeting_title, logo_str)
    

    
    #html_summary_title = re.sub(r"<p><strong>", "<h1>", html_summary_split[0])
    #html_summary_title = re.sub(r"</strong></p>", "</h1>", html_summary_title)
    #rest_of_summary = "\n".join(html_summary_split[1:])
    
    #html_summary_final = f"""
    #<div class="main-header">
    #    {html_summary_title}
    #</div>
    #<div class="box-content">
    #    {rest_of_summary}
    #</div>
    #"""


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

    html_client_industry_sources = format_sources_to_html(client_industry_sources, 'Client Industry News')
    html_client_holdings_sources = format_holdings_to_html(client_holdings_sources, 'Client Holdings News')
    html_macro_news_sources = format_sources_to_html(macro_news_sources, 'Macro Economic News')


    full_html = f"""
    <html>
    <head>
        <meta charset='UTF-8'>
        <title>{meeting_title}</title>
        <style>
            .main-header {{
                font-weight: bold;
                font-size: 24px;
                margin-bottom: 20px;
                color: #2980B9;
            }}
            body,p, ul, ol, li, div {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 10px
                margin: 30px auto;
                color: #333;
                line-height: 1.6;
                max-width: 800px;
            }}
            body {{
                margin: 15px auto;
                max-width: 800px;
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
            h4 {{
                color: #2980B9;
                font-size: 10px;
                margin-top: 2px;
                margin-bottom: 2px;
            }}
            ul {{
                padding-left: 20px;
            }}
            ul.objectives-list li {{
                font-size: 12px;
                margin-bottom: 8px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 4px;
            }}
            th, td {{
                text-align: left;
                padding: 12px;
                font-size: 10px;
            }}
            th {{
                background-color: #f1f1f1;
                color: #2980B9;
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
            .box-content {{
                margin-top: 20px;
                padding: 20px;
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
            }}
            .sources-section {{
                margin-top: 10px;
                padding: 10px;
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
            }}
            .article {{
                margin-bottom: 10px;
            }}
            .article h4 {{
                color: #2980B9;
                font-size: 8px;
            }}
            .article p {{
                font-size: 8px;
                line-height: 1.4;
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
        </style>
    </head>
    <body>
        {html_summary_final}

        <h2>Macro-Economic Snapshot</h2>
        <div class="box-content">
            {financial_snapshot_html}
        </div>

        <h2>Resources</h2>
        <div class="box-content">
            {html_client_industry_sources}
            {html_client_holdings_sources}
            {html_macro_news_sources}
        </div>

    </body>
    </html>
    """

    return full_html

    

def generate_short_report(result):
    meeting_title = result.get('meeting_description', '') + ' : Briefing Document'
    final_summary = result.get('final_summary', '')
    client_holdings_sources = result.get('client_holdings_sources', list())
    client_industry_sources = result.get('client_industry_sources', list())
    macro_news_sources = result.get('macro_news_sources', list())
    logo_str = get_logo()

    #Summary section
    bullet_points = final_summary.strip().split('•')
    bullet_points = [point.strip() for point in bullet_points if point.strip()]
    html_bullets = ''.join(f'<li>{point}</li>' for point in bullet_points)

    # Format source sections
    html_client_industry_sources = format_sources_to_html(client_industry_sources, 'Client Industry News')
    html_client_holdings_sources = format_holdings_to_html(client_holdings_sources, 'Client Holdings News')
    html_macro_news_sources = format_sources_to_html(macro_news_sources, 'Macro Economic News')

    # Summary section with "See Sources" button
          #  <img src="{logo_str}" class="logo" alt="Logo">
    html_summary_final = f"""
    <div class="box-content">
        <h1>{meeting_title}</h1>
        <ul>
            {html_bullets}
        </ul>
        <button onclick="toggleResources()" style="margin-top: 10px;">See Sources</button>
    </div>
    """

    # Hidden Resources section
    resources_html = f"""
    <div id="resources-content" class="box-content" style="display:none;">
        <h2>Resources</h2>
        {html_client_industry_sources}
        {html_client_holdings_sources}
        {html_macro_news_sources}
    </div>
    """

    # Full HTML with toggle script
    full_html = f"""
    <html>
    <head>
        <meta charset='UTF-8'>
        <title>{meeting_title}</title>
        <style>
            body, p, ul, ol, li, div {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 15px;
                color: #333;
                line-height: 1.6;
                max-width: 800px;
                margin: 30px auto;
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
                padding: 20px;
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
            .box-content {{
                margin-top: 15px;
                padding: 10px;
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
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
        </style>
        <script>
            function toggleResources() {{
                var content = document.getElementById('resources-content');
                if (content.style.display === 'none') {{
                    content.style.display = 'block';
                }} else {{
                    content.style.display = 'none';
                }}
            }}
        </script>
    </head>
    <body>
        {html_summary_final}
        {resources_html}
    </body>
    </html>
    """

    return full_html








def generate_med_report(result):
    meeting_title = result.get('meeting_description', '') + ' : Briefing Document'
    client_holdings_sources = result.get('client_holdings_sources', list())
    client_industry_sources = result.get('client_industry_sources', list())
    macro_news_sources = result.get('macro_news_sources', list())
    final_summary = result.get('final_summary', '')
    client_company = result.get('client_company', '')
    logo_str = get_logo()
    email_summary = result.get('email_summary', '')
    recent_email_summar = result.get('recent_email_summary', '')
    recent_client_questions = result.get('recent_client_questions', '')

    # HTML for the toggle boxes
    toggle_boxes_html = f"""
<div class="box-content">
    <div style="margin-top: 12px; margin-bottom: 12px;">
        <button onclick="toggleBox('overall-box')">Overall</button>
        <button onclick="toggleBox('recent-email-box')">Recent Email</button>
        <button onclick="toggleBox('client-questions-box')">Client Questions</button>
    </div>
    <div id='overall-box' class='box-content' style='display:none;'>{email_summary}</div>
    <div id='recent-email-box' class='box-content' style='display:none;'>{recent_email_summar}</div>
    <div id='client-questions-box' class='box-content' style='display:none;'>{recent_client_questions}</div>
</div>
"""

    # Insert the toggle boxes right before section 2
    final_summary_with_boxes = re.sub(
        r"(?=\n*\*\*2\. Financial Overview\*\*)", 
        f"\n\n{toggle_boxes_html}\n\n", 
        final_summary,
        count = 1
    )

    # Convert markdown to HTML
    html_summary_final = format_paragraph_summary_to_html(final_summary_with_boxes, meeting_title, logo_str)

    # Source sections
    html_client_industry_sources = format_sources_to_html(client_industry_sources, 'Client Industry News')
    html_client_holdings_sources = format_holdings_to_html(client_holdings_sources, 'Client Holdings News')
    html_macro_news_sources = format_sources_to_html(macro_news_sources, 'Macro Economic News')

    # Hidden Resources section
    resources_html = f"""
    <div id="resources-content" class="box-content" style="display:none;">
        <h2>Resources</h2>
        {html_client_industry_sources}
        {html_client_holdings_sources}
        {html_macro_news_sources}
    </div>
    """

    # Full HTML document
    full_html = f"""
    <html>
    <head>
        <meta charset='UTF-8'>
        <title>{meeting_title}</title>
        <style>
            body, p, ul, ol, li, div {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 15px;
                color: #333;
                line-height: 1.6;
                max-width: 800px;
                margin: 30px auto;
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
                padding: 20px;
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
        </style>
        <script>
            function toggleResources() {{
                var content = document.getElementById('resources-content');
                content.style.display = content.style.display === 'none' ? 'block' : 'none';
            }}
            function toggleBox(id) {{
                const allBoxes = ['overall-box', 'recent-email-box', 'client-questions-box'];
                allBoxes.forEach(boxId => {{
                    document.getElementById(boxId).style.display = (boxId === id) ?
                        (document.getElementById(boxId).style.display === 'none' ? 'block' : 'none') :
                        'none';
                }});
            }}
        </script>
    </head>
    <body>
        {html_summary_final}
        {resources_html}
    </body>
    </html>
    """

    return full_html




def save_html_to_file (html_content: str, filename: str):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)


def convert_html_to_pdf(html_string, output_pdf):
    weasyprint.HTML(string=html_string).write_pdf(
        output_pdf,
        stylesheets=None,
        presentational_hints=True,
        page_size='Letter',
    )


if __name__ == "__main__":
    generate_long_report(dict())
