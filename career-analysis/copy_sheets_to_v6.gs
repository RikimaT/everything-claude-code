function copySheets() {
  // コピー元：アップロードしたファイル
  var sourceId = '1hVseP-7hQyNQoixcPBapt9sYh7u071fm8581azH3Oec';
  var source = SpreadsheetApp.openById(sourceId);

  // コピー先：このスプレッドシート（v6）
  var target = SpreadsheetApp.getActiveSpreadsheet();

  // コピーするシート名リスト
  var sheetNames = [
    '中学校補正マスタ',
    '換算マスタ',
    'テスト点数入力＆進学先予測',
    'OCR読取データ',
    '定期テスト×進学先 相関分析'
  ];

  for (var i = 0; i < sheetNames.length; i++) {
    var sheet = source.getSheetByName(sheetNames[i]);
    if (sheet) {
      sheet.copyTo(target).setName(sheetNames[i]);
      Logger.log(sheetNames[i] + ' をコピーしました');
    } else {
      Logger.log(sheetNames[i] + ' が見つかりませんでした');
    }
  }

  SpreadsheetApp.getUi().alert('全シートのコピーが完了しました！');
}
