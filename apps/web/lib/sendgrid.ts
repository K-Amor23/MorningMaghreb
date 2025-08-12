import sgMail from '@sendgrid/mail';

// Initialize SendGrid with API key
sgMail.setApiKey(process.env.SENDGRID_API_KEY!);

export interface EmailData {
  to: string;
  subject: string;
  html: string;
  text?: string;
  from?: string;
}

export interface NewsletterData {
  to: string;
  subject: string;
  marketMovers: any[];
  corporateActions: any[];
  macroHighlights: any[];
  aiCommentary: string;
}

export class SendGridService {
  private static fromEmail = process.env.SENDGRID_FROM_EMAIL || 'noreply@casablancainsights.com';

  /**
   * Send a basic email
   */
  static async sendEmail(emailData: EmailData): Promise<boolean> {
    try {
      const msg = {
        to: emailData.to,
        from: emailData.from || this.fromEmail,
        subject: emailData.subject,
        html: emailData.html,
        text: emailData.text || this.stripHtml(emailData.html),
      };

      await sgMail.send(msg);
      console.log(`Email sent successfully to ${emailData.to}`);
      return true;
    } catch (error) {
      console.error('SendGrid error:', error);
      return false;
    }
  }

  /**
   * Send the Morning Maghreb newsletter
   */
  static async sendNewsletter(newsletterData: NewsletterData): Promise<boolean> {
    const html = this.generateNewsletterHTML(newsletterData);
    const text = this.generateNewsletterText(newsletterData);

    return this.sendEmail({
      to: newsletterData.to,
      subject: newsletterData.subject,
      html,
      text,
    });
  }

  /**
   * Send price alerts
   */
  static async sendPriceAlert(
    to: string,
    symbol: string,
    currentPrice: number,
    alertPrice: number,
    alertType: 'above' | 'below'
  ): Promise<boolean> {
    const subject = `Price Alert: ${symbol} ${alertType} ${alertPrice}`;
    const html = `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #2563eb;">🚨 Price Alert</h2>
        <p><strong>Symbol:</strong> ${symbol}</p>
        <p><strong>Current Price:</strong> ${currentPrice} MAD</p>
        <p><strong>Alert Price:</strong> ${alertPrice} MAD</p>
        <p><strong>Alert Type:</strong> ${alertType === 'above' ? 'Above' : 'Below'}</p>
        <hr>
        <p style="font-size: 12px; color: #666;">
          This alert was triggered by your price monitoring settings on Casablanca Insights.
        </p>
      </div>
    `;

    return this.sendEmail({
      to,
      subject,
      html,
    });
  }

  /**
   * Send contest notifications
   */
  static async sendContestNotification(
    to: string,
    contestName: string,
    message: string,
    actionUrl?: string
  ): Promise<boolean> {
    const subject = `Contest Update: ${contestName}`;
    const html = `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #059669;">🏆 Contest Update</h2>
        <h3>${contestName}</h3>
        <p>${message}</p>
        ${actionUrl ? `<p><a href="${actionUrl}" style="background: #2563eb; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Contest</a></p>` : ''}
        <hr>
        <p style="font-size: 12px; color: #666;">
          You're receiving this because you're participating in trading contests on Casablanca Insights.
        </p>
      </div>
    `;

    return this.sendEmail({
      to,
      subject,
      html,
    });
  }

  /**
   * Generate newsletter HTML
   */
  private static generateNewsletterHTML(data: NewsletterData): string {
    return `
      <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; background: #f8fafc;">
        <div style="background: #1e293b; color: white; padding: 20px; text-align: center;">
          <h1 style="margin: 0; font-size: 28px;">🌅 Morning Maghreb</h1>
          <p style="margin: 10px 0 0 0; opacity: 0.9;">Your Daily Market Digest</p>
        </div>
        
        <div style="padding: 30px; background: white;">
          ${data.marketMovers.length > 0 ? `
            <h2 style="color: #2563eb; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px;">📈 Top Market Movers</h2>
            <div style="margin: 20px 0;">
              ${data.marketMovers.map((mover: any) => `
                <div style="padding: 15px; border: 1px solid #e2e8f0; margin: 10px 0; border-radius: 5px;">
                  <strong>${mover.symbol}</strong> - ${mover.name}<br>
                  <span style="color: ${mover.change >= 0 ? '#059669' : '#dc2626'};">
                    ${mover.change >= 0 ? '+' : ''}${mover.change}% (${mover.price} MAD)
                  </span>
                </div>
              `).join('')}
            </div>
          ` : ''}
          
          ${data.corporateActions.length > 0 ? `
            <h2 style="color: #7c3aed; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px;">🏢 Corporate Actions</h2>
            <div style="margin: 20px 0;">
              ${data.corporateActions.map((action: any) => `
                <div style="padding: 15px; border: 1px solid #e2e8f0; margin: 10px 0; border-radius: 5px;">
                  <strong>${action.company}</strong><br>
                  ${action.action} - ${action.date}
                </div>
              `).join('')}
            </div>
          ` : ''}
          
          ${data.macroHighlights.length > 0 ? `
            <h2 style="color: #ea580c; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px;">📊 Macro Highlights</h2>
            <div style="margin: 20px 0;">
              ${data.macroHighlights.map((highlight: any) => `
                <div style="padding: 15px; border: 1px solid #e2e8f0; margin: 10px 0; border-radius: 5px;">
                  <strong>${highlight.indicator}</strong><br>
                  ${highlight.value} (${highlight.change})
                </div>
              `).join('')}
            </div>
          ` : ''}
          
          ${data.aiCommentary ? `
            <h2 style="color: #059669; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px;">🤖 AI Commentary</h2>
            <div style="margin: 20px 0; padding: 20px; background: #f0f9ff; border-radius: 5px;">
              <p style="margin: 0; line-height: 1.6;">${data.aiCommentary}</p>
            </div>
          ` : ''}
        </div>
        
        <div style="background: #1e293b; color: white; padding: 20px; text-align: center;">
          <p style="margin: 0; font-size: 14px;">
            Powered by Casablanca Insights | 
            <a href="https://casablancainsights.com" style="color: #60a5fa;">Visit Website</a> |
            <a href="https://casablancainsights.com/unsubscribe" style="color: #60a5fa;">Unsubscribe</a>
          </p>
        </div>
      </div>
    `;
  }

  /**
   * Generate newsletter text version
   */
  private static generateNewsletterText(data: NewsletterData): string {
    let text = 'Morning Maghreb - Your Daily Market Digest\n\n';
    
    if (data.marketMovers.length > 0) {
      text += 'TOP MARKET MOVERS:\n';
      data.marketMovers.forEach((mover: any) => {
        text += `${mover.symbol} - ${mover.name}: ${mover.change >= 0 ? '+' : ''}${mover.change}% (${mover.price} MAD)\n`;
      });
      text += '\n';
    }
    
    if (data.corporateActions.length > 0) {
      text += 'CORPORATE ACTIONS:\n';
      data.corporateActions.forEach((action: any) => {
        text += `${action.company}: ${action.action} - ${action.date}\n`;
      });
      text += '\n';
    }
    
    if (data.macroHighlights.length > 0) {
      text += 'MACRO HIGHLIGHTS:\n';
      data.macroHighlights.forEach((highlight: any) => {
        text += `${highlight.indicator}: ${highlight.value} (${highlight.change})\n`;
      });
      text += '\n';
    }
    
    if (data.aiCommentary) {
      text += `AI COMMENTARY:\n${data.aiCommentary}\n\n`;
    }
    
    text += 'Powered by Casablanca Insights\n';
    text += 'Visit: https://casablancainsights.com\n';
    text += 'Unsubscribe: https://casablancainsights.com/unsubscribe';
    
    return text;
  }

  /**
   * Strip HTML tags for text version
   */
  private static stripHtml(html: string): string {
    return html.replace(/<[^>]*>/g, '');
  }
} 