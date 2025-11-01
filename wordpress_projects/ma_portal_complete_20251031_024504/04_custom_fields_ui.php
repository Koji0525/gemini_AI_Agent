<?php
/**
 * カスタムフィールドUI - ACF不要版
 * 投稿編集画面に美しいフィールドを自動表示
 */

// カスタムメタボックスを追加
function ma_add_custom_meta_boxes() {
    add_meta_box(
        'ma_company_details',
        '�� 企業詳細情報',
        'ma_render_company_details_box',
        'ma_company',
        'normal',
        'high'
    );
}
add_action('add_meta_boxes', 'ma_add_custom_meta_boxes');

// メタボックスの内容を表示
function ma_render_company_details_box($post) {
    wp_nonce_field('ma_save_company_details', 'ma_company_details_nonce');
    
    $location = get_post_meta($post->ID, 'location', true);
    $capital = get_post_meta($post->ID, 'capital', true);
    $employees = get_post_meta($post->ID, 'employees', true);
    $revenue = get_post_meta($post->ID, 'revenue', true);
    $deal_type = get_post_meta($post->ID, 'deal_type', true);
    ?>
    
    <style>
    .ma-field-group {
        margin-bottom: 20px;
    }
    .ma-field-group label {
        display: block;
        font-weight: bold;
        margin-bottom: 8px;
        color: #23282d;
    }
    .ma-field-group input,
    .ma-field-group select {
        width: 100%;
        padding: 8px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 14px;
    }
    .ma-field-group small {
        display: block;
        margin-top: 5px;
        color: #666;
    }
    </style>
    
    <div class="ma-field-group">
        <label>📍 所在地 <span style="color:red;">*</span></label>
        <input type="text" name="location" value="<?php echo esc_attr($location); ?>" placeholder="例: 東京都渋谷区" required>
        <small>都道府県から入力してください</small>
    </div>
    
    <div class="ma-field-group">
        <label>💰 資本金（万円） <span style="color:red;">*</span></label>
        <input type="number" name="capital" value="<?php echo esc_attr($capital); ?>" placeholder="例: 10000" required>
        <small>万円単位で入力してください</small>
    </div>
    
    <div class="ma-field-group">
        <label>👥 従業員数 <span style="color:red;">*</span></label>
        <input type="number" name="employees" value="<?php echo esc_attr($employees); ?>" placeholder="例: 50" required>
        <small>正社員の人数を入力してください</small>
    </div>
    
    <div class="ma-field-group">
        <label>📊 年商（万円） <span style="color:red;">*</span></label>
        <input type="number" name="revenue" value="<?php echo esc_attr($revenue); ?>" placeholder="例: 100000" required>
        <small>年間売上を万円単位で入力してください</small>
    </div>
    
    <div class="ma-field-group">
        <label>🤝 希望条件 <span style="color:red;">*</span></label>
        <select name="deal_type" required>
            <option value="">選択してください</option>
            <option value="売却希望" <?php selected($deal_type, '売却希望'); ?>>売却希望</option>
            <option value="買収希望" <?php selected($deal_type, '買収希望'); ?>>買収希望</option>
            <option value="提携希望" <?php selected($deal_type, '提携希望'); ?>>提携希望</option>
        </select>
    </div>
    <?php
}

// データを保存
function ma_save_company_details($post_id) {
    if (!isset($_POST['ma_company_details_nonce'])) return;
    if (!wp_verify_nonce($_POST['ma_company_details_nonce'], 'ma_save_company_details')) return;
    if (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) return;
    if (!current_user_can('edit_post', $post_id)) return;
    
    $fields = ['location', 'capital', 'employees', 'revenue', 'deal_type'];
    
    foreach ($fields as $field) {
        if (isset($_POST[$field])) {
            update_post_meta($post_id, $field, sanitize_text_field($_POST[$field]));
        }
    }
}
add_action('save_post_ma_company', 'ma_save_company_details');
?>
