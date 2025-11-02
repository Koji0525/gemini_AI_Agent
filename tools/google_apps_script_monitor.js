/**
 * Google Apps Script: システム異常検知
 * 
 * スプレッドシートに設定して、1時間ごとに実行
 */

function checkSystemHealth() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // 1. 失敗タスクのチェック
  const tasksSheet = ss.getSheetByName('pm_tasks');
  const tasksData = tasksSheet.getDataRange().getValues();
  
  let failedCount = 0;
  for (let i = 1; i < tasksData.length; i++) {
    if (tasksData[i][3] === 'failed') {
      failedCount++;
    }
  }
  
  // 2. 長期実行中タスクのチェック
  let longRunningCount = 0;
  for (let i = 1; i < tasksData.length; i++) {
    if (tasksData[i][3] === 'in_progress') {
      longRunningCount++;
    }
  }
  
  // 3. エラーログのチェック
  const errorSheet = ss.getSheetByName('error_analysis');
  const errorData = errorSheet.getDataRange().getValues();
  
  let unresolvedErrors = 0;
  for (let i = 1; i < errorData.length; i++) {
    if (errorData[i][3] !== 'resolved') {
      unresolvedErrors++;
    }
  }
  
  // アラート判定
  const alerts = [];
  
  if (failedCount > 5) {
    alerts.push(`�� 失敗タスクが${failedCount}件あります`);
  }
  
  if (longRunningCount > 3) {
    alerts.push(`⚠️ 長期実行中のタスクが${longRunningCount}件あります`);
  }
  
  if (unresolvedErrors > 10) {
    alerts.push(`⚠️ 未解決エラーが${unresolvedErrors}件あります`);
  }
  
  // アラート送信
  if (alerts.length > 0) {
    const message = alerts.join('\n');
    
    // メール送信
    MailApp.sendEmail({
      to: 'your-email@example.com',
      subject: '🚨 24時間自律開発システム アラート',
      body: `システム異常を検知しました:\n\n${message}\n\nスプレッドシートを確認してください。`
    });
    
    // Slack通知（Webhook URLを設定）
    const slackWebhook = 'YOUR_SLACK_WEBHOOK_URL';
    const payload = {
      text: '🚨 システム異常検知',
      blocks: [
        {
          type: 'section',
          text: {
            type: 'mrkdwn',
            text: message
          }
        }
      ]
    };
    
    UrlFetchApp.fetch(slackWebhook, {
      method: 'post',
      contentType: 'application/json',
      payload: JSON.stringify(payload)
    });
  }
}

/**
 * トリガー設定用関数
 * スクリプトエディタで1度実行してトリガーを作成
 */
function setupTrigger() {
  // 既存のトリガーを削除
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(trigger => ScriptApp.deleteTrigger(trigger));
  
  // 1時間ごとのトリガーを作成
  ScriptApp.newTrigger('checkSystemHealth')
    .timeBased()
    .everyHours(1)
    .create();
  
  Logger.log('トリガー設定完了: 1時間ごとに実行');
}
