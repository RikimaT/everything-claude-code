/**
 * @file Staff.gs
 * スタッフ操作関連
 *
 * [v41 修正] getMonthlyRecords が null を返すバグの修正
 *
 * 根本原因の可能性（優先順）:
 *  - 仮説D: Fix.gs / Payroll.gs 等に同名 getMonthlyRecords が存在 → そちらが呼ばれる
 *    確認: GAS エディタで Ctrl+Shift+F → "function getMonthlyRecords" を全ファイル検索
 *    対策: 重複定義を削除し、この Staff.gs の定義のみにする
 *  - 仮説A: フロントの params.staffId が undefined → Staff.gs の catch が反応するはずだが、
 *    仮説D と組み合わさると別関数の undefined return → null になる
 *    対策: StaffApp.html の loadHistory() で currentStaff.staffId を明示的に渡す
 *  - 仮説C: catchブロック内で二次例外 → google.script.run が null を返す
 *    対策: catchブロックを最小化
 */

/**
 * スタッフログイン認証
 * @param {{staffId: string}} params
 */
function loginStaff(params) {
  try {
    if (!params || !params.staffId) {
      return { success: false, error: 'staffIdが必要です' };
    }
    var ss    = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(CONFIG.SHEETS.STAFF);
    if (!sheet) return { success: false, error: 'スタッフマスタが見つかりません: ' + CONFIG.SHEETS.STAFF };

    var data = sheet.getDataRange().getValues();
    var id   = String(params.staffId).trim().toUpperCase();

    for (var i = 1; i < data.length; i++) {
      var row    = data[i];
      var rowId  = String(row[CONFIG.STAFF_COL.STAFF_ID] || '').trim().toUpperCase();
      var status = String(row[CONFIG.STAFF_COL.STATUS]   || '').trim().toLowerCase();

      if (rowId !== id) continue;
      if (status !== 'active') return { success: false, error: 'このスタッフIDは無効です' };

      return {
        success: true,
        staff: {
          staffId: String(row[CONFIG.STAFF_COL.STAFF_ID]).trim(),
          name:    String(row[CONFIG.STAFF_COL.NAME]    ).trim(),
          email:   String(row[CONFIG.STAFF_COL.EMAIL]   ).trim()
        }
      };
    }
    return { success: false, error: 'スタッフIDが見つかりません: ' + params.staffId };
  } catch (e) {
    return { success: false, error: String(e) };
  }
}

/**
 * スタッフ月次記録取得
 *
 * @param {{staffId:string, year?:number, month?:number}} params
 * @returns {{success:boolean, records:Array, error?:string}}
 *
 * !! IMPORTANT !! この関数は Staff.gs にのみ定義すること。
 * Fix.gs / Payroll.gs 等に同名関数があると GAS グローバルスコープで上書きされ
 * フロントへ null が返る (仮説D)。全ファイルで検索して重複を削除すること。
 */
function getMonthlyRecords(params) {
  try {
    // 仮説A対策: params 存在確認
    if (!params || typeof params !== 'object') {
      return {
        success: false,
        error: 'params が null/undefined: ' + JSON.stringify(params),
        records: []
      };
    }

    // staffId は複数キー名に対応（フロント実装の揺れを吸収）
    var staffId = params.staffId || params.id || params.staff_id;
    if (!staffId) {
      return {
        success: false,
        error: 'staffId が未指定。受信キー: ' + Object.keys(params).join(', '),
        records: []
      };
    }
    staffId = String(staffId).trim();

    var now   = new Date();
    var year  = Number(params.year)  || now.getFullYear();
    var month = Number(params.month) || (now.getMonth() + 1);

    var ss    = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(CONFIG.SHEETS.ATTENDANCE);
    if (!sheet) {
      return { success: false, error: 'シートが見つかりません: ' + CONFIG.SHEETS.ATTENDANCE, records: [] };
    }

    var data    = sheet.getDataRange().getValues();
    var records = [];

    for (var i = 1; i < data.length; i++) {
      var row      = data[i];
      var rowStaff = String(row[CONFIG.ATT_COL.STAFF_ID] || '').trim();
      if (rowStaff !== staffId) continue;

      var dateRaw = row[CONFIG.ATT_COL.DATE];
      if (!dateRaw) continue;

      var d = (dateRaw instanceof Date) ? dateRaw : new Date(dateRaw);
      if (isNaN(d.getTime())) continue;
      if (d.getFullYear() !== year || (d.getMonth() + 1) !== month) continue;

      records.push({
        date:     Utilities.formatDate(d, CONFIG.TIMEZONE, 'yyyy/MM/dd'),
        clockIn:  _timeValToStr(row[CONFIG.ATT_COL.CLOCK_IN]),
        clockOut: _timeValToStr(row[CONFIG.ATT_COL.CLOCK_OUT]),
        note:     String(row[CONFIG.ATT_COL.NOTE] || '')
      });
    }

    records.sort(function(a, b) { return a.date < b.date ? -1 : a.date > b.date ? 1 : 0; });

    return { success: true, records: records };

  } catch (e) {
    // 仮説C対策: catch 内で追加の変数参照・処理を一切行わない
    return { success: false, error: String(e), records: [] };
  }
}

/** @private Date または時刻セル値を HH:mm 文字列へ変換 */
function _timeValToStr(val) {
  if (!val) return '';
  if (val instanceof Date) return Utilities.formatDate(val, CONFIG.TIMEZONE, 'HH:mm');
  return String(val);
}

/**
 * 診断用: GAS エディタの実行ボタンで直接テスト
 * ログに STF001 の4月データが出れば getMonthlyRecords 自体は正常
 */
function _runDiagHistory() {
  var result = getMonthlyRecords({ staffId: 'STF001', year: 2026, month: 4 });
  Logger.log(JSON.stringify(result));
}
