import os

FROM_EMAIL = os.environ.get("RESEND_FROM_EMAIL", "One17 <chtan@one-17.com>")

GROUP_PROMPTS = {
    "Your operations": "Worth checking with whoever runs facilities/site ops \u2014 these are often "
                        "physically present but not tracked centrally.",
    "Your energy": "Usually confirmed against a utility bill or meter \u2014 worth a quick check with finance/ops.",
    "Your value chain": "Often sits with procurement, HR, or logistics rather than facilities \u2014 "
                         "worth checking which team actually holds this data.",
}


def build_report_html(payload: dict) -> str:
    sector = payload.get("sector", "your sector")
    s1 = payload.get("scope1_present", 0)
    s2 = payload.get("scope2_present", 0)
    s3 = payload.get("scope3_present", 0)
    unsure_items = payload.get("unsure_items", []) or []
    answers = payload.get("answers", {})

    unsure_rows = ""
    if unsure_items:
        for name in unsure_items:
            unsure_rows += (
                f'<tr><td style="padding:10px 0;border-bottom:1px solid #D5D5D1;">'
                f'<p style="margin:0 0 4px;font-size:14px;color:#3D3D3D;font-weight:700;">{name}</p>'
                f'<p style="margin:0;font-size:13px;color:#5C5C59;">'
                f'Worth confirming with the relevant team \u2014 sources marked unsure are the most common '
                f'place a completeness gap hides.</p></td></tr>'
            )
    else:
        unsure_rows = (
            '<tr><td style="padding:10px 0;"><p style="margin:0;font-size:14px;color:#5C5C59;">'
            'No unsure items \u2014 you had a clear present/absent answer for everything screened.</p></td></tr>'
        )

    html = f"""
    <div style="font-family:'DM Sans',Arial,sans-serif;background:#F5F5F3;padding:32px 16px;">
      <div style="max-width:560px;margin:0 auto;background:#ffffff;border:1px solid #D5D5D1;">
        <div style="background:#3D3D3D;padding:20px 24px;">
          <p style="margin:0;color:#ffffff;font-size:15px;font-weight:700;">OneCarbon by One17</p>
          <p style="margin:2px 0 0;color:#C9C9C6;font-size:12px;">GHG completeness screening report</p>
        </div>
        <div style="padding:24px;">
          <p style="margin:0 0 4px;font-size:11px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#5C7D5F;">Sector</p>
          <p style="margin:0 0 20px;font-size:16px;color:#3D3D3D;">{sector}</p>

          <p style="margin:0 0 8px;font-size:11px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#5C7D5F;">Sources present, by scope</p>
          <table role="presentation" style="width:100%;border-collapse:collapse;margin-bottom:20px;">
            <tr>
              <td style="background:#F5F5F3;padding:12px;text-align:center;border:1px solid #D5D5D1;">
                <p style="margin:0;font-size:11px;color:#8A8A87;">Scope 1</p>
                <p style="margin:2px 0 0;font-size:20px;font-weight:700;color:#3D3D3D;">{s1}</p>
              </td>
              <td style="width:8px;"></td>
              <td style="background:#F5F5F3;padding:12px;text-align:center;border:1px solid #D5D5D1;">
                <p style="margin:0;font-size:11px;color:#8A8A87;">Scope 2</p>
                <p style="margin:2px 0 0;font-size:20px;font-weight:700;color:#3D3D3D;">{s2}</p>
              </td>
              <td style="width:8px;"></td>
              <td style="background:#F5F5F3;padding:12px;text-align:center;border:1px solid #D5D5D1;">
                <p style="margin:0;font-size:11px;color:#8A8A87;">Scope 3</p>
                <p style="margin:2px 0 0;font-size:20px;font-weight:700;color:#3D3D3D;">{s3}</p>
              </td>
            </tr>
          </table>

          <p style="margin:0 0 8px;font-size:11px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#B06A4F;">Marked unsure \u2014 check these first</p>
          <table role="presentation" style="width:100%;border-collapse:collapse;margin-bottom:20px;">
            {unsure_rows}
          </table>

          <div style="background:#F5F5F3;padding:16px;margin-bottom:20px;border-left:3px solid #B06A4F;">
            <p style="margin:0;font-size:13px;color:#5C5C59;">
              This check doesn't screen every possible source \u2014 categories like franchises, financed
              emissions, and processing of sold products are left out here. A full assessment covers these too.
            </p>
          </div>

          <p style="margin:0 0 20px;font-size:14px;color:#5C5C59;line-height:1.6;">
            One more thing worth knowing: marking a source "present" is just the first step. Each present
            source still needs a materiality assessment, a boundary decision, and a data quality rating
            before it's something a verifier would sign off on. That's the part a self-check can't do for you.
          </p>

          <a href="https://one-17.com" style="display:inline-block;background:#7A9E7E;color:#ffffff;
             text-decoration:none;font-size:14px;font-weight:700;padding:12px 20px;">
             Talk to a verifier about this
          </a>
        </div>
        <div style="padding:16px 24px;border-top:1px solid #D5D5D1;">
          <p style="margin:0;font-size:11px;color:#8A8A87;">One17 Pte Ltd &middot; Sustainability &amp; Carbon Advisory &middot; Singapore &amp; APAC</p>
        </div>
      </div>
    </div>
    """
    return html


def send_report_email(to_email: str, payload: dict) -> dict:
    import resend

    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        raise RuntimeError("RESEND_API_KEY not set")
    resend.api_key = api_key

    sector = payload.get("sector", "your business")
    html = build_report_html(payload)

    return resend.Emails.send({
        "from": FROM_EMAIL,
        "to": [to_email],
        "subject": f"Your GHG completeness check \u2014 {sector}",
        "html": html,
        "reply_to": "chtan@one-17.com",
    })
