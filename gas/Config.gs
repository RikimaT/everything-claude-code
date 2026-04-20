/**
 * @file Config.gs
 * ブリッジ勤怠管理システム - 設定定数
 */
var CONFIG = {
  SHEETS: {
    STAFF:      'スタッフマスタ',
    ATTENDANCE: '出退勤ログ',
    PAYROLL:    '給与計算',
    SETTINGS:   '設定'
  },

  // スタッフマスタ 列インデックス (0始まり)
  STAFF_COL: {
    STAFF_ID:   0,
    NAME:       1,
    EMAIL:      2,
    PHONE:      3,
    STATUS:     4,  // 'active' / 'inactive'
    HOURLY:     5
  },

  // 出退勤ログ 列インデックス (0始まり)
  ATT_COL: {
    DATE:       0,
    STAFF_ID:   1,
    STAFF_NAME: 2,
    CLOCK_IN:   3,
    CLOCK_OUT:  4,
    WORK_HOURS: 5,
    NOTE:       6
  },

  ADMIN_EMAILS: ['rikima81@gmail.com', 'ec010007yuka@gmail.com'],

  TIMEZONE: 'Asia/Tokyo'
};
