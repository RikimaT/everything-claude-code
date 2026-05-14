// =============================================================
// 自習室 入退室管理システム - バックエンド (Code.gs)
// =============================================================

// ★★★ 必ず設定してください ★★★
var CONFIG = {
  // Google スプレッドシートのID（URLの /d/xxxxx/edit の xxxxx 部分）
  SPREADSHEET_ID: 'YOUR_SPREADSHEET_ID_HERE',

  // シート名（スプレッドシートのタブ名と一致させること）
  LOG_SHEET_NAME: '入退室ログ',
  MASTER_SHEET_NAME: '生徒マスタ',

  // 管理者メールアドレス（必ず通知が届くアドレスを設定）
  ADMIN_EMAIL: 'admin@example.com',

  // システム表示名
  SYSTEM_NAME: '自習室入退室管理システム',

  // タイムゾーン
  TIMEZONE: 'Asia/Tokyo'
};

// -------------------------------------------------------------
// GETリクエスト: HTMLページを返す
// -------------------------------------------------------------
function doGet(e) {
  return HtmlService.createHtmlOutputFromFile('index')
    .setTitle('自習室 入退室打刻')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

// -------------------------------------------------------------
// POSTリクエスト: 打刻データを受け取り処理する
// -------------------------------------------------------------
function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var studentId = (data.studentId || '').toString().trim();
    var action = (data.action || '').toString().trim(); // '入室' or '退室'

    // 入力バリデーション
    if (!studentId) {
      return jsonResponse(false, '生徒IDが未入力です。');
    }
    if (action !== '入室' && action !== '退室') {
      return jsonResponse(false, '区分が不正です（入室または退室を指定）。');
    }

    // 生徒マスタ検索
    var studentInfo = getStudentInfo(studentId);
    if (!studentInfo) {
      return jsonResponse(false, '生徒ID「' + studentId + '」が見つかりません。管理者にお問い合わせください。');
    }

    // ログ記録
    var timestamp = new Date();
    recordLog(studentInfo, action, timestamp);

    // メール通知
    sendNotificationEmail(studentInfo, action, timestamp);

    var timestampStr = Utilities.formatDate(timestamp, CONFIG.TIMEZONE, 'yyyy/MM/dd HH:mm:ss');
    return jsonResponse(true,
      studentInfo.name + ' さんの' + action + 'を記録しました。',
      { studentName: studentInfo.name, action: action, timestamp: timestampStr }
    );

  } catch (err) {
    Logger.log('doPost error: ' + err.message);
    return jsonResponse(false, 'システムエラーが発生しました。管理者に連絡してください。(詳細: ' + err.message + ')');
  }
}

// -------------------------------------------------------------
// 生徒マスタから生徒情報を取得
// -------------------------------------------------------------
function getStudentInfo(studentId) {
  var ss = SpreadsheetApp.openById(CONFIG.SPREADSHEET_ID);
  var sheet = ss.getSheetByName(CONFIG.MASTER_SHEET_NAME);
  if (!sheet) {
    throw new Error('生徒マスタシートが見つかりません: ' + CONFIG.MASTER_SHEET_NAME);
  }

  var data = sheet.getDataRange().getValues();
  // ヘッダー行をスキップ（i=1から）
  for (var i = 1; i < data.length; i++) {
    if (String(data[i][0]).trim() === String(studentId).trim()) {
      return {
        id:          String(data[i][0]).trim(),
        name:        String(data[i][1]).trim(),
        parentEmail: String(data[i][2]).trim(),
        note:        data[i][3] ? String(data[i][3]).trim() : ''
      };
    }
  }
  return null;
}

// -------------------------------------------------------------
// 入退室ログシートに記録
// -------------------------------------------------------------
function recordLog(studentInfo, action, timestamp) {
  var ss = SpreadsheetApp.openById(CONFIG.SPREADSHEET_ID);
  var sheet = ss.getSheetByName(CONFIG.LOG_SHEET_NAME);
  if (!sheet) {
    throw new Error('入退室ログシートが見つかりません: ' + CONFIG.LOG_SHEET_NAME);
  }

  var dateStr = Utilities.formatDate(timestamp, CONFIG.TIMEZONE, 'yyyy/MM/dd');
  var timeStr = Utilities.formatDate(timestamp, CONFIG.TIMEZONE, 'HH:mm:ss');
  var dayOfWeek = ['日','月','火','水','木','金','土'][timestamp.getDay()];

  // カラム順: タイムスタンプ | 生徒ID | 氏名 | 区分 | 日付 | 曜日 | 時刻
  sheet.appendRow([
    timestamp,
    studentInfo.id,
    studentInfo.name,
    action,
    dateStr,
    dayOfWeek,
    timeStr
  ]);
}

// -------------------------------------------------------------
// 保護者・管理者へHTMLメール送信
// -------------------------------------------------------------
function sendNotificationEmail(studentInfo, action, timestamp) {
  var dateTimeStr = Utilities.formatDate(timestamp, CONFIG.TIMEZONE, 'yyyy年MM月dd日（E） HH:mm');
  var actionColor = (action === '入室') ? '#27AE60' : '#E74C3C';
  var actionBg    = (action === '入室') ? '#EAFAF1' : '#FDEDEC';
  var actionIcon  = (action === '入室') ? '✅ 入室' : '👋 退室';

  var subject = '【' + CONFIG.SYSTEM_NAME + '】' + studentInfo.name + ' さんが' + action + 'しました';

  var htmlBody = '<!DOCTYPE html>\n'
    + '<html lang="ja"><head>\n'
    + '<meta charset="UTF-8">\n'
    + '<meta name="viewport" content="width=device-width,initial-scale=1.0">\n'
    + '<style>\n'
    + '  body{margin:0;padding:0;background:#f0f2f5;font-family:"Helvetica Neue",Arial,sans-serif;}\n'
    + '  .wrap{max-width:580px;margin:24px auto;background:#fff;border-radius:16px;'
    + '        overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.12);}\n'
    + '  .hd{background:' + actionColor + ';padding:36px 24px;text-align:center;color:#fff;}\n'
    + '  .hd h1{margin:0 0 8px;font-size:22px;font-weight:700;}\n'
    + '  .badge{display:inline-block;background:rgba(255,255,255,.22);border-radius:999px;'
    + '         padding:10px 32px;font-size:26px;font-weight:900;letter-spacing:2px;}\n'
    + '  .bd{padding:28px 24px;background:' + actionBg + ';}\n'
    + '  table{width:100%;border-collapse:collapse;}\n'
    + '  td{padding:13px 16px;border-bottom:1px solid #e0e0e0;font-size:15px;}\n'
    + '  td.lbl{color:#888;font-weight:600;width:38%;background:#fafafa;}\n'
    + '  td.val{color:#222;font-weight:700;}\n'
    + '  .action-cell{color:' + actionColor + ';font-size:20px;}\n'
    + '  .ft{padding:18px 24px;text-align:center;color:#bbb;font-size:12px;background:#f9f9f9;border-top:1px solid #eee;}\n'
    + '</style></head>\n'
    + '<body><div class="wrap">\n'
    + '  <div class="hd">\n'
    + '    <h1>' + CONFIG.SYSTEM_NAME + '</h1>\n'
    + '    <div class="badge">' + actionIcon + '</div>\n'
    + '  </div>\n'
    + '  <div class="bd">\n'
    + '    <table>\n'
    + '      <tr><td class="lbl">生徒名</td><td class="val">' + studentInfo.name + ' さん</td></tr>\n'
    + '      <tr><td class="lbl">生徒ID</td><td class="val">' + studentInfo.id + '</td></tr>\n'
    + '      <tr><td class="lbl">区分</td><td class="val action-cell">' + action + '</td></tr>\n'
    + '      <tr><td class="lbl">日時</td><td class="val">' + dateTimeStr + '</td></tr>\n'
    + '    </table>\n'
    + '  </div>\n'
    + '  <div class="ft">このメールは ' + CONFIG.SYSTEM_NAME + ' から自動送信されています。</div>\n'
    + '</div></body></html>';

  // 送信先リストを構築（重複を除去）
  var recipients = {};
  recipients[CONFIG.ADMIN_EMAIL] = true;
  if (studentInfo.parentEmail && studentInfo.parentEmail !== '') {
    recipients[studentInfo.parentEmail] = true;
  }

  Object.keys(recipients).forEach(function(email) {
    try {
      GmailApp.sendEmail(email, subject, '（このメールはHTML対応メールクライアントでご確認ください）', {
        htmlBody: htmlBody,
        name: CONFIG.SYSTEM_NAME
      });
    } catch (mailErr) {
      Logger.log('メール送信失敗 (' + email + '): ' + mailErr.message);
    }
  });
}

// -------------------------------------------------------------
// ヘルパー: JSON レスポンスを生成
// -------------------------------------------------------------
function jsonResponse(success, message, extra) {
  var payload = { success: success, message: message };
  if (extra) {
    Object.keys(extra).forEach(function(k) { payload[k] = extra[k]; });
  }
  return ContentService
    .createTextOutput(JSON.stringify(payload))
    .setMimeType(ContentService.MimeType.JSON);
}

// -------------------------------------------------------------
// 【初回セットアップ用】スプレッドシートのヘッダーを自動作成
// GASエディタから手動で一度だけ実行してください
// -------------------------------------------------------------
function setupSheets() {
  var ss = SpreadsheetApp.openById(CONFIG.SPREADSHEET_ID);

  // 入退室ログシート
  var logSheet = ss.getSheetByName(CONFIG.LOG_SHEET_NAME)
               || ss.insertSheet(CONFIG.LOG_SHEET_NAME);
  if (logSheet.getLastRow() === 0) {
    logSheet.appendRow(['タイムスタンプ', '生徒ID', '氏名', '区分', '日付', '曜日', '時刻']);
    logSheet.getRange(1, 1, 1, 7).setFontWeight('bold').setBackground('#34495E').setFontColor('#FFFFFF');
    logSheet.setFrozenRows(1);
  }

  // 生徒マスタシート
  var masterSheet = ss.getSheetByName(CONFIG.MASTER_SHEET_NAME)
                  || ss.insertSheet(CONFIG.MASTER_SHEET_NAME);
  if (masterSheet.getLastRow() === 0) {
    masterSheet.appendRow(['生徒ID', '氏名', '保護者メールアドレス', '備考']);
    masterSheet.getRange(1, 1, 1, 4).setFontWeight('bold').setBackground('#2C3E50').setFontColor('#FFFFFF');
    masterSheet.setFrozenRows(1);
    // サンプルデータ
    masterSheet.appendRow(['S001', '山田 太郎', 'parent_yamada@example.com', '']);
    masterSheet.appendRow(['S002', '佐藤 花子', 'parent_sato@example.com', '']);
  }

  SpreadsheetApp.flush();
  Logger.log('セットアップ完了！');
}
