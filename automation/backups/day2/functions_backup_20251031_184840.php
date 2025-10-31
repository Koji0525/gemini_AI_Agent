<?php
// Cocoon Child Theme Functions - Google翻訳 + DeepL翻訳対応_251003

// ===== APIキー設定（ここだけ変更すればOK！）=====
define('UZBEK_GOOGLE_TRANSLATE_API_KEY', 'AIzaSyDZuaYw16s_FCPugHkWnhvBoAog0E1X3vE');
define('UZBEK_DEEPL_API_KEY', '7c7ba8ad-f11b-4c68-8baf-e1d7864f6ee6:fx'); // DeepL API Key

// 翻訳エンジン選択: 'google' または 'deepl'
// ※ウズベク語(uz)はDeepL非対応のため、自動的にGoogleを使用します
define('UZBEK_TRANSLATION_ENGINE', 'deepl'); // 'google' or 'deepl'

// DeepL APIタイプ: 'free' または 'pro'
define('UZBEK_DEEPL_API_TYPE', 'free'); // 'free' or 'pro'

// 処理中フラグ（重複実行防止用）
global $uzbek_translation_in_progress;
$uzbek_translation_in_progress = false;

// 改良版ログ関数（複数の場所に記録）
function uzbek_debug_log($message) {
    $timestamp = date('Y-m-d H:i:s');
    $log_message = "[{$timestamp}] UZBEK_TRANSLATION: {$message}";
    
    // 1. WordPress標準のエラーログに記録
    error_log($log_message);
    
    // 2. 独自ログファイルに記録（パーミッション問題対策）
    $log_file = WP_CONTENT_DIR . '/uzbek-translation-debug.log';
    
    // ディレクトリの書き込み権限確認
    if (is_writable(WP_CONTENT_DIR)) {
        $log_entry = $log_message . PHP_EOL;
        file_put_contents($log_file, $log_entry, FILE_APPEND | LOCK_EX);
    }
    
    // 3. データベースに一時保存（確実な方法）
    $existing_logs = get_option('uzbek_debug_logs', array());
    $existing_logs[] = array(
        'timestamp' => $timestamp,
        'message' => $message
    );
    
    // 最新50件のみ保持
    if (count($existing_logs) > 50) {
        $existing_logs = array_slice($existing_logs, -50);
    }
    
    update_option('uzbek_debug_logs', $existing_logs);
}

// DeepL翻訳API呼び出し関数
function uzbek_translate_with_deepl($text, $target_lang, $api_key) {
    if (empty($text) || empty(trim($text))) {
        uzbek_debug_log("翻訳対象テキストが空です");
        return '';
    }
    
    // DeepLのエンドポイント
    $api_type = UZBEK_DEEPL_API_TYPE;
    $api_url = ($api_type === 'free') 
        ? 'https://api-free.deepl.com/v2/translate' 
        : 'https://api.deepl.com/v2/translate';
    
    // DeepL用言語コード変換
    $deepl_lang_map = array(
        'en' => 'EN-US',  // 英語（アメリカ）
        'ru' => 'RU',     // ロシア語
        'zh-CN' => 'ZH',  // 中国語（簡体字）
        'ko' => 'KO',     // 韓国語
        'tr' => 'TR'      // トルコ語
    );
    
    $deepl_target = isset($deepl_lang_map[$target_lang]) ? $deepl_lang_map[$target_lang] : $target_lang;
    
    uzbek_debug_log("DeepL翻訳開始: " . substr($text, 0, 50) . " -> {$deepl_target}");
    
    $response = wp_remote_post($api_url, array(
        'body' => array(
            'auth_key' => $api_key,
            'text' => $text,
            'source_lang' => 'JA',
            'target_lang' => $deepl_target,
            'tag_handling' => 'html'  // HTMLタグを保持
        ),
        'timeout' => 30
    ));
    
    if (is_wp_error($response)) {
        uzbek_debug_log("DeepL翻訳APIエラー: " . $response->get_error_message());
        return false;
    }
    
    $response_code = wp_remote_retrieve_response_code($response);
    if ($response_code !== 200) {
        uzbek_debug_log("DeepL翻訳HTTPエラー ({$response_code}): " . wp_remote_retrieve_body($response));
        return false;
    }
    
    $data = json_decode(wp_remote_retrieve_body($response), true);
    
    if (isset($data['translations'][0]['text'])) {
        $translated = $data['translations'][0]['text'];
        uzbek_debug_log("DeepL翻訳成功: " . substr($translated, 0, 50));
        return $translated;
    }
    
    uzbek_debug_log("DeepL翻訳レスポンス解析失敗: " . wp_remote_retrieve_body($response));
    return false;
}

// Google翻訳API呼び出し関数
function uzbek_translate_with_google($text, $target_lang, $api_key, $format = 'text') {
    if (empty($text) || empty(trim($text))) {
        uzbek_debug_log("翻訳対象テキストが空です");
        return '';
    }
    
    $api_url = 'https://translation.googleapis.com/language/translate/v2';
    
    uzbek_debug_log("Google翻訳開始: " . substr($text, 0, 50) . " -> {$target_lang}");
    
    $response = wp_remote_post($api_url . '?key=' . $api_key, array(
        'body' => json_encode(array(
            'q' => $text,
            'source' => 'ja',
            'target' => $target_lang,
            'format' => $format
        )),
        'headers' => array('Content-Type' => 'application/json'),
        'timeout' => 30
    ));
    
    if (is_wp_error($response)) {
        uzbek_debug_log("Google翻訳APIエラー: " . $response->get_error_message());
        return false;
    }
    
    $response_code = wp_remote_retrieve_response_code($response);
    if ($response_code !== 200) {
        uzbek_debug_log("Google翻訳HTTPエラー ({$response_code}): " . wp_remote_retrieve_body($response));
        return false;
    }
    
    $data = json_decode(wp_remote_retrieve_body($response), true);
    
    if (isset($data['data']['translations'][0]['translatedText'])) {
        $translated = $data['data']['translations'][0]['translatedText'];
        uzbek_debug_log("Google翻訳成功: " . substr($translated, 0, 50));
        return $translated;
    }
    
    uzbek_debug_log("Google翻訳レスポンス解析失敗: " . wp_remote_retrieve_body($response));
    return false;
}

// 統合翻訳関数（エンジン自動選択）
function uzbek_translate_text($text, $target_lang, $format = 'text') {
    $engine = UZBEK_TRANSLATION_ENGINE;
    
    // ウズベク語の場合は強制的にGoogle翻訳を使用
    if ($target_lang === 'uz') {
        uzbek_debug_log("ウズベク語のためGoogle翻訳を使用");
        $google_key = UZBEK_GOOGLE_TRANSLATE_API_KEY;
        if (empty($google_key) || $google_key === 'ここに実際のAPIキーを貼り付け') {
            uzbek_debug_log("エラー: Google APIキーが設定されていません");
            return false;
        }
        return uzbek_translate_with_google($text, $target_lang, $google_key, $format);
    }
    
    // それ以外の言語は設定に従う
    if ($engine === 'deepl') {
        $deepl_key = UZBEK_DEEPL_API_KEY;
        if (empty($deepl_key) || $deepl_key === 'ここにDeepL APIキーを貼り付け') {
            uzbek_debug_log("警告: DeepL APIキー未設定のためGoogle翻訳を使用");
            $google_key = UZBEK_GOOGLE_TRANSLATE_API_KEY;
            return uzbek_translate_with_google($text, $target_lang, $google_key, $format);
        }
        return uzbek_translate_with_deepl($text, $target_lang, $deepl_key);
    } else {
        $google_key = UZBEK_GOOGLE_TRANSLATE_API_KEY;
        if (empty($google_key) || $google_key === 'ここに実際のAPIキーを貼り付け') {
            uzbek_debug_log("エラー: Google APIキーが設定されていません");
            return false;
        }
        return uzbek_translate_with_google($text, $target_lang, $google_key, $format);
    }
}

// ログ表示画面（改良版）
function uzbek_show_debug_log() {
    if (!current_user_can('manage_options')) return;
    
    echo '<div class="wrap">';
    echo '<h1>翻訳デバッグログ</h1>';
    
    // ログクリアボタン
    if (isset($_POST['clear_log'])) {
        delete_option('uzbek_debug_logs');
        delete_option('uzbek_translation_processed');
        $log_file = WP_CONTENT_DIR . '/uzbek-translation-debug.log';
        if (file_exists($log_file)) {
            file_put_contents($log_file, '');
        }
        echo '<div class="notice notice-success"><p>ログをクリアしました。</p></div>';
    }
    
    // テスト実行ボタン
    if (isset($_POST['test_translation'])) {
        uzbek_manual_translation_test_inline();
    }
    
    // メタデータチェックボタン
    if (isset($_POST['check_meta'])) {
        uzbek_check_post_metadata();
    }
    
    echo '<form method="post" style="margin-bottom: 20px;">';
    echo '<select name="test_type" style="margin-right: 10px;">';
    echo '<option value="post">投稿をテスト</option>';
    echo '<option value="page">固定ページをテスト</option>';
    echo '</select>';
    echo '<input type="submit" name="test_translation" class="button button-primary" value="翻訳テストを実行">';
    echo ' <input type="submit" name="check_meta" class="button" value="メタデータをチェック">';
    echo ' <input type="submit" name="clear_log" class="button" value="ログをクリア" onclick="return confirm(\'ログを削除しますか？\')">';
    echo '</form>';
    
    // データベースからログ取得
    $db_logs = get_option('uzbek_debug_logs', array());
    
    if (!empty($db_logs)) {
        echo '<h3>最新のログ（データベース）</h3>';
        echo '<textarea readonly style="width: 100%; height: 300px; font-family: monospace; font-size: 12px;">';
        foreach ($db_logs as $log_entry) {
            echo esc_textarea("[{$log_entry['timestamp']}] {$log_entry['message']}\n");
        }
        echo '</textarea>';
    }
    
    // ファイルからログ取得
    $log_file = WP_CONTENT_DIR . '/uzbek-translation-debug.log';
    if (file_exists($log_file)) {
        $log_content = file_get_contents($log_file);
        if (!empty($log_content)) {
            $lines = explode("\n", $log_content);
            $recent_lines = array_slice($lines, -30);
            $recent_content = implode("\n", $recent_lines);
            
            echo '<h3>最新のログ（ファイル）</h3>';
            echo '<textarea readonly style="width: 100%; height: 200px; font-family: monospace; font-size: 12px;">';
            echo esc_textarea($recent_content);
            echo '</textarea>';
        }
    }
    
    // システム情報表示
    echo '<h3>システム情報</h3>';
    echo '<ul>';
    echo '<li><strong>wp-content書き込み権限:</strong> ' . (is_writable(WP_CONTENT_DIR) ? '✅ OK' : '❌ NG') . '</li>';
    echo '<li><strong>ログファイル存在:</strong> ' . (file_exists($log_file) ? '✅ あり' : '❌ なし') . '</li>';
    echo '<li><strong>ログファイルパス:</strong> ' . $log_file . '</li>';
    
    // 翻訳エンジン表示
    $engine = UZBEK_TRANSLATION_ENGINE;
    $engine_display = ($engine === 'deepl') ? '🔵 DeepL' : '🟢 Google翻訳';
    echo '<li><strong>翻訳エンジン:</strong> ' . $engine_display . '</li>';
    
    // Google APIキー
    $google_key = UZBEK_GOOGLE_TRANSLATE_API_KEY;
    $google_status = (empty($google_key) || $google_key === 'ここに実際のAPIキーを貼り付け') ? '❌ 未設定' : '✅ 設定済み';
    echo '<li><strong>Google APIキー:</strong> ' . $google_status . '</li>';
    
    // DeepL APIキー
    $deepl_key = UZBEK_DEEPL_API_KEY;
    $deepl_status = (empty($deepl_key) || $deepl_key === 'ここにDeepL APIキーを貼り付け') ? '❌ 未設定' : '✅ 設定済み';
    echo '<li><strong>DeepL APIキー:</strong> ' . $deepl_status . '</li>';
    
    // DeepL APIタイプ
    $api_type = UZBEK_DEEPL_API_TYPE;
    echo '<li><strong>DeepL APIタイプ:</strong> ' . strtoupper($api_type) . '</li>';
    
    echo '<li><strong>Polylang:</strong> ' . (function_exists('pll_get_post_language') ? '✅ 有効' : '❌ 無効') . '</li>';
    
    // SEOプラグインチェック
    $seo_plugin = 'なし';
    if (defined('WPSEO_VERSION')) {
        $seo_plugin = 'Yoast SEO';
    } elseif (defined('AIOSEO_VERSION')) {
        $seo_plugin = 'All in One SEO';
    } elseif (function_exists('seopress_activation')) {
        $seo_plugin = 'SEOPress';
    }
    echo '<li><strong>SEOプラグイン:</strong> ' . $seo_plugin . '</li>';
    
    echo '</ul>';
    
    // 対応言語表示
    echo '<h3>翻訳対象言語</h3>';
    echo '<ul>';
    echo '<li>🇬🇧 英語 (en) - ' . ($engine === 'deepl' ? 'DeepL対応' : 'Google翻訳') . '</li>';
    echo '<li>🇷🇺 ロシア語 (ru) - ' . ($engine === 'deepl' ? 'DeepL対応' : 'Google翻訳') . '</li>';
    echo '<li>🇺🇿 ウズベク語 (uz) - Google翻訳のみ（DeepL非対応）</li>';
    echo '<li>🇨🇳 中国語 (zh-CN) - ' . ($engine === 'deepl' ? 'DeepL対応' : 'Google翻訳') . '</li>';
    echo '<li>🇰🇷 韓国語 (ko) - ' . ($engine === 'deepl' ? 'DeepL対応' : 'Google翻訳') . '</li>';
    echo '<li>🇹🇷 トルコ語 (tr) - ' . ($engine === 'deepl' ? 'DeepL対応' : 'Google翻訳') . '</li>';
    echo '</ul>';
    
    // 対応投稿タイプ表示
    echo '<h3>対応投稿タイプ</h3>';
    echo '<ul>';
    echo '<li>📝 投稿 (post)</li>';
    echo '<li>📄 固定ページ (page)</li>';
    echo '</ul>';
    
    // 処理済み投稿リスト
    $processed = get_option('uzbek_translation_processed', array());
    if (!empty($processed)) {
        echo '<h3>処理済み投稿ID</h3>';
        echo '<p>' . implode(', ', array_slice($processed, -20)) . '...</p>';
    }
    
    if (empty($db_logs) && !file_exists($log_file)) {
        echo '<div class="notice notice-warning"><p>ログがありません。「翻訳テストを実行」ボタンを押してログを生成してください。</p></div>';
    }
    
    echo '</div>';
}

// インラインテスト関数（投稿・固定ページ対応）
function uzbek_manual_translation_test_inline() {
    uzbek_debug_log("=== 手動翻訳テスト開始 ===");
    
    // テスト対象の選択（投稿または固定ページ）
    $test_type = isset($_POST['test_type']) ? $_POST['test_type'] : 'post';
    
    if ($test_type === 'page') {
        $recent_items = get_pages(array(
            'number' => 1,
            'sort_order' => 'desc',
            'sort_column' => 'post_date',
            'post_status' => 'publish'
        ));
        
        if (!empty($recent_items)) {
            $post_id = $recent_items[0]->ID;
            uzbek_debug_log("テスト対象固定ページID: {$post_id} - タイトル: " . $recent_items[0]->post_title);
        } else {
            uzbek_debug_log("❌ エラー: テスト用の固定ページが見つかりません");
            echo '<div class="notice notice-error"><p>テスト用の固定ページが見つかりません。</p></div>';
            return;
        }
    } else {
        $recent_posts = wp_get_recent_posts(array(
            'numberposts' => 1,
            'post_status' => 'publish',
            'post_type' => 'post'
        ));
        
        if (!empty($recent_posts)) {
            $post_id = $recent_posts[0]['ID'];
            uzbek_debug_log("テスト対象投稿ID: {$post_id} - タイトル: " . $recent_posts[0]['post_title']);
        } else {
            uzbek_debug_log("❌ エラー: テスト用の投稿が見つかりません");
            echo '<div class="notice notice-error"><p>テスト用の投稿が見つかりません。</p></div>';
            return;
        }
    }
    
    // APIキーチェック
    $engine = UZBEK_TRANSLATION_ENGINE;
    if ($engine === 'deepl') {
        $api_key = UZBEK_DEEPL_API_KEY;
        if (empty($api_key) || $api_key === 'ここにDeepL APIキーを貼り付け') {
            uzbek_debug_log("❌ エラー: DeepL APIキーが設定されていません");
            echo '<div class="notice notice-error"><p>DeepL APIキーが設定されていません。functions.phpの6行目を確認してください。</p></div>';
            return;
        }
        uzbek_debug_log("✅ DeepL APIキー設定確認OK");
    } else {
        $api_key = UZBEK_GOOGLE_TRANSLATE_API_KEY;
        if (empty($api_key) || $api_key === 'ここに実際のAPIキーを貼り付け') {
            uzbek_debug_log("❌ エラー: Google APIキーが設定されていません");
            echo '<div class="notice notice-error"><p>Google APIキーが設定されていません。functions.phpの5行目を確認してください。</p></div>';
            return;
        }
        uzbek_debug_log("✅ Google APIキー設定確認OK");
    }
    
    // Polylangチェック
    if (!function_exists('pll_get_post_language')) {
        uzbek_debug_log("❌ エラー: Polylangプラグインが無効です");
        echo '<div class="notice notice-error"><p>Polylangプラグインが無効です。</p></div>';
        return;
    }
    
    uzbek_debug_log("✅ Polylang確認OK");
    
    // 処理済みフラグをクリア
    $processed = get_option('uzbek_translation_processed', array());
    $key = array_search($post_id, $processed);
    if ($key !== false) {
        unset($processed[$key]);
        update_option('uzbek_translation_processed', $processed);
    }
    
    // 翻訳実行
    uzbek_process_translation_immediate($post_id);
    
    echo '<div class="notice notice-success"><p>翻訳テストを実行しました。上記のログを確認してください。</p></div>';
}

// メタデータチェック関数
function uzbek_check_post_metadata() {
    uzbek_debug_log("=== メタデータチェック開始 ===");
    
    $recent_posts = wp_get_recent_posts(array(
        'numberposts' => 1,
        'post_status' => 'publish',
        'post_type' => 'post'
    ));
    
    if (empty($recent_posts)) {
        echo '<div class="notice notice-error"><p>投稿が見つかりません。</p></div>';
        return;
    }
    
    $post_id = $recent_posts[0]['ID'];
    $post_title = $recent_posts[0]['post_title'];
    
    echo '<div class="notice notice-info">';
    echo '<h3>投稿のメタデータ分析</h3>';
    echo '<p><strong>投稿タイトル:</strong> ' . esc_html($post_title) . ' (ID: ' . $post_id . ')</p>';
    
    $all_meta = get_post_meta($post_id);
    
    echo '<h4>SEO関連メタデータ:</h4>';
    echo '<table style="width:100%; border-collapse: collapse;">';
    echo '<tr style="background:#f0f0f0;"><th style="padding:5px; text-align:left; border:1px solid #ddd;">メタキー</th><th style="padding:5px; text-align:left; border:1px solid #ddd;">値</th></tr>';
    
    $seo_found = false;
    
    foreach ($all_meta as $key => $value) {
        if (strpos(strtolower($key), 'seo') !== false || 
            strpos(strtolower($key), 'description') !== false || 
            strpos(strtolower($key), 'keyword') !== false || 
            strpos(strtolower($key), 'title') !== false ||
            strpos(strtolower($key), 'the_page') !== false ||
            strpos(strtolower($key), 'yoast') !== false ||
            strpos(strtolower($key), 'aioseo') !== false ||
            strpos(strtolower($key), 'seopress') !== false) {
            
            $display_value = is_array($value) ? $value[0] : $value;
            if (!empty($display_value) && !is_serialized($display_value)) {
                echo '<tr>';
                echo '<td style="padding:5px; border:1px solid #ddd; font-family:monospace;">' . esc_html($key) . '</td>';
                echo '<td style="padding:5px; border:1px solid #ddd;">' . esc_html(substr($display_value, 0, 200)) . '</td>';
                echo '</tr>';
                $seo_found = true;
                
                uzbek_debug_log("メタデータ発見: {$key} = " . substr($display_value, 0, 100));
            }
        }
    }
    
    if (!$seo_found) {
        echo '<tr><td colspan="2" style="padding:5px; border:1px solid #ddd;">SEO関連のメタデータが見つかりません</td></tr>';
    }
    
    echo '</table>';
    
    echo '<h4>タグ情報:</h4>';
    $tags = wp_get_post_tags($post_id);
    if (!empty($tags)) {
        echo '<ul>';
        foreach ($tags as $tag) {
            echo '<li>' . esc_html($tag->name) . ' (ID: ' . $tag->term_id . ')</li>';
            uzbek_debug_log("タグ: {$tag->name} (ID: {$tag->term_id})");
        }
        echo '</ul>';
    } else {
        echo '<p>タグが設定されていません</p>';
        uzbek_debug_log("タグが設定されていません");
    }
    
    echo '</div>';
    
    uzbek_debug_log("=== メタデータチェック終了 ===");
}

// 管理画面メニューに追加
function uzbek_add_debug_menu() {
    add_management_page(
        '翻訳デバッグログ',
        '翻訳ログ',
        'manage_options',
        'uzbek-debug-log',
        'uzbek_show_debug_log'
    );
}
add_action('admin_menu', 'uzbek_add_debug_menu');

// 即座に翻訳を実行する版（投稿・固定ページ対応）
function uzbek_immediate_auto_translate($post_id, $post, $update) {
    global $uzbek_translation_in_progress;
    
    if ($uzbek_translation_in_progress) {
        uzbek_debug_log("スキップ: 翻訳処理中");
        return;
    }
    
    uzbek_debug_log("=== 自動翻訳処理開始: Post ID {$post_id} ===");
    
    try {
        if (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) {
            uzbek_debug_log("スキップ: 自動保存中");
            return;
        }
        if (wp_is_post_revision($post_id)) {
            uzbek_debug_log("スキップ: リビジョン");
            return;
        }
        if ($post->post_status !== 'publish') {
            uzbek_debug_log("スキップ: ステータスが '{$post->post_status}'");
            return;
        }
        
        if (!in_array($post->post_type, array('post', 'page'))) {
            uzbek_debug_log("スキップ: 投稿タイプが '{$post->post_type}'");
            return;
        }
        
        $processed = get_option('uzbek_translation_processed', array());
        if (in_array($post_id, $processed)) {
            uzbek_debug_log("スキップ: この投稿は既に処理済み");
            return;
        }
        
        if (!function_exists('pll_get_post_language')) {
            uzbek_debug_log("エラー: Polylang関数が利用できません");
            return;
        }
        
        $post_language = pll_get_post_language($post_id);
        uzbek_debug_log("投稿言語: {$post_language}");
        
        if ($post_language !== 'ja') {
            uzbek_debug_log("スキップ: 日本語以外の投稿");
            return;
        }
        
        if (function_exists('pll_get_post_translations')) {
            $translations = pll_get_post_translations($post_id);
            uzbek_debug_log("既存翻訳: " . json_encode($translations));
            
            if (count($translations) > 1) {
                uzbek_debug_log("スキップ: 既に翻訳が存在");
                return;
            }
        }
        
        uzbek_debug_log("翻訳処理開始");
        
        $uzbek_translation_in_progress = true;
        
        $processed[] = $post_id;
        update_option('uzbek_translation_processed', $processed);
        
        uzbek_process_translation_immediate($post_id);
        
        $uzbek_translation_in_progress = false;
        
    } catch (Exception $e) {
        $uzbek_translation_in_progress = false;
        uzbek_debug_log("例外エラー: " . $e->getMessage());
    }
    
    uzbek_debug_log("=== 自動翻訳処理終了 ===");
}

// 翻訳処理実行
function uzbek_process_translation_immediate($post_id) {
    $post = get_post($post_id);
    if (!$post) {
        uzbek_debug_log("エラー: 投稿が見つかりません");
        return;
    }
    
    uzbek_debug_log("投稿タイプ: {$post->post_type} - タイトル: " . substr($post->post_title, 0, 50) . "...");
    
    $languages = array(
        'en' => '英語',
        'ru' => 'ロシア語',
        'uz' => 'ウズベク語',
        'zh-CN' => '中国語',
        'ko' => '韓国語',
        'tr' => 'トルコ語'
    );
    
    remove_action('save_post', 'uzbek_immediate_auto_translate', 20);
    
    $success_count = 0;
    $total_languages = count($languages);
    $all_translations = array();
    $all_translations['ja'] = $post_id;
    
    foreach ($languages as $lang => $lang_name) {
        uzbek_debug_log("--- {$lang_name}翻訳開始 ({$lang}) ---");
        
        $pll_lang = ($lang === 'zh-CN') ? 'zh' : $lang;
        
        $new_post_id = uzbek_create_translation_debug($post_id, $post, $lang, $pll_lang);
        
        if ($new_post_id) {
            uzbek_debug_log("✅ {$lang_name}翻訳成功: 新投稿ID {$new_post_id}");
            $all_translations[$pll_lang] = $new_post_id;
            $success_count++;
        } else {
            uzbek_debug_log("❌ {$lang_name}翻訳失敗");
        }
    }
    
    if (function_exists('pll_save_post_translations') && count($all_translations) > 1) {
        pll_save_post_translations($all_translations);
        uzbek_debug_log("全翻訳関係設定完了: " . json_encode($all_translations));
    }
    
    add_action('save_post', 'uzbek_immediate_auto_translate', 20, 3);
    
    uzbek_debug_log("翻訳完了: {$success_count}/{$total_languages} 言語の翻訳に成功");
}

// カテゴリーの翻訳と設定
function uzbek_translate_and_set_categories($original_id, $new_post_id, $target_lang, $pll_lang) {
    $post_type = get_post_type($original_id);
    
    if ($post_type === 'page') {
        uzbek_debug_log("固定ページのためカテゴリー処理をスキップ");
        return;
    }
    
    $categories = wp_get_post_categories($original_id);
    if (empty($categories)) {
        uzbek_debug_log("カテゴリーなし");
        return;
    }
    
    $translated_cat_ids = array();
    
    foreach ($categories as $cat_id) {
        $original_cat = get_category($cat_id);
        if (!$original_cat) continue;
        
        if (function_exists('pll_get_term')) {
            $translated_cat_id = pll_get_term($cat_id, $pll_lang);
            
            if (!$translated_cat_id) {
                $translated_name = uzbek_translate_text($original_cat->name, $target_lang);
                $translated_slug = sanitize_title($translated_name);
                
                if ($translated_name) {
                    $new_cat = wp_insert_term(
                        $translated_name,
                        'category',
                        array(
                            'slug' => $translated_slug,
                            'parent' => 0
                        )
                    );
                    
                    if (!is_wp_error($new_cat)) {
                        $translated_cat_id = $new_cat['term_id'];
                        
                        if (function_exists('pll_set_term_language')) {
                            pll_set_term_language($translated_cat_id, $pll_lang);
                        }
                        
                        if (function_exists('pll_save_term_translations')) {
                            $cat_translations = pll_get_term_translations($cat_id);
                            $cat_translations['ja'] = $cat_id;
                            $cat_translations[$pll_lang] = $translated_cat_id;
                            pll_save_term_translations($cat_translations);
                        }
                        
                        uzbek_debug_log("カテゴリー翻訳作成: {$original_cat->name} → {$translated_name}");
                    }
                }
            }
            
            if ($translated_cat_id) {
                $translated_cat_ids[] = $translated_cat_id;
            }
        }
    }
    
    if (!empty($translated_cat_ids)) {
        wp_set_post_categories($new_post_id, $translated_cat_ids);
        uzbek_debug_log("カテゴリー設定完了: " . count($translated_cat_ids) . "個");
    }
}

// タグの翻訳と設定
function uzbek_translate_and_set_tags($original_id, $new_post_id, $target_lang, $pll_lang) {
    uzbek_debug_log("=== タグ翻訳処理開始 ===");
    
    $tags = wp_get_post_tags($original_id);
    if (empty($tags)) {
        uzbek_debug_log("タグなし");
        return;
    }
    
    uzbek_debug_log("元投稿のタグ数: " . count($tags));
    
    $translated_tag_names = array();
    $successful_translations = 0;
    
    foreach ($tags as $tag) {
        uzbek_debug_log("処理中のタグ: {$tag->name} (ID: {$tag->term_id})");
        
        $translated_name = uzbek_translate_text($tag->name, $target_lang);
        
        if ($translated_name && !empty(trim($translated_name))) {
            $translated_tag_names[] = trim($translated_name);
            uzbek_debug_log("タグ翻訳成功: {$tag->name} → {$translated_name}");
            $successful_translations++;
        } else {
            uzbek_debug_log("タグ翻訳失敗: {$tag->name}");
        }
        
        usleep(200000);
    }
    
    if (!empty($translated_tag_names)) {
        $result = wp_set_post_tags($new_post_id, $translated_tag_names, false);
        
        if (is_wp_error($result)) {
            uzbek_debug_log("タグ設定エラー: " . $result->get_error_message());
        } else {
            uzbek_debug_log("タグ設定完了: {$successful_translations}個のタグを設定");
            
            $new_tags = wp_get_post_tags($new_post_id);
            if (!empty($new_tags)) {
                uzbek_debug_log("設定確認: " . count($new_tags) . "個のタグが正常に設定されました");
                foreach ($new_tags as $new_tag) {
                    uzbek_debug_log("設定済みタグ: {$new_tag->name}");
                }
            }
        }
    } else {
        uzbek_debug_log("翻訳に成功したタグがありません");
    }
    
    uzbek_debug_log("=== タグ翻訳処理終了 ===");
}

// SEOメタデータの翻訳と設定
function uzbek_translate_and_set_seo_meta($original_id, $new_post_id, $target_lang) {
    uzbek_debug_log("=== SEOメタデータ翻訳開始 ===");
    
    $all_meta = get_post_meta($original_id);
    uzbek_debug_log("=== 元投稿のメタデータ一覧 ===");
    
    $found_seo_meta = false;
    foreach ($all_meta as $key => $value) {
        if (strpos($key, 'seo') !== false || strpos($key, 'description') !== false || 
            strpos($key, 'keyword') !== false || strpos($key, 'title') !== false ||
            strpos($key, 'the_page') !== false) {
            $display_value = is_array($value) ? $value[0] : $value;
            if (!empty($display_value)) {
                uzbek_debug_log("メタキー: {$key} = " . substr($display_value, 0, 100));
                $found_seo_meta = true;
            }
        }
    }
    
    if (!$found_seo_meta) {
        uzbek_debug_log("SEOメタデータが見つかりません");
    }
    
    $translated_count = 0;
    
    // Cocoonテーマ対応
    $cocoon_seo_title = get_post_meta($original_id, 'the_page_seo_title', true);
    $cocoon_meta_desc = get_post_meta($original_id, 'the_page_meta_description', true);
    $cocoon_meta_keywords = get_post_meta($original_id, 'the_page_meta_keywords', true);
    
    if (!empty($cocoon_seo_title) || !empty($cocoon_meta_desc) || !empty($cocoon_meta_keywords)) {
        uzbek_debug_log("Cocoonテーマのメタデータを検出");
        
        if (!empty($cocoon_seo_title)) {
            uzbek_debug_log("Cocoon SEOタイトル翻訳開始: " . substr($cocoon_seo_title, 0, 50));
            $translated_title = uzbek_translate_text($cocoon_seo_title, $target_lang);
            if ($translated_title) {
                update_post_meta($new_post_id, 'the_page_seo_title', $translated_title);
                uzbek_debug_log("Cocoon SEOタイトル翻訳完了: " . substr($translated_title, 0, 50));
                $translated_count++;
            } else {
                uzbek_debug_log("Cocoon SEOタイトル翻訳失敗");
            }
            usleep(200000);
        }
        
        if (!empty($cocoon_meta_desc)) {
            uzbek_debug_log("Cocoon メタディスクリプション翻訳開始: " . substr($cocoon_meta_desc, 0, 50));
            $translated_desc = uzbek_translate_text($cocoon_meta_desc, $target_lang);
            if ($translated_desc) {
                update_post_meta($new_post_id, 'the_page_meta_description', $translated_desc);
                uzbek_debug_log("Cocoon メタディスクリプション翻訳完了");
                $translated_count++;
            } else {
                uzbek_debug_log("Cocoon メタディスクリプション翻訳失敗");
            }
            usleep(200000);
        }
        
        if (!empty($cocoon_meta_keywords)) {
            uzbek_debug_log("Cocoon メタキーワード翻訳開始: " . substr($cocoon_meta_keywords, 0, 50));
            $translated_keywords = uzbek_translate_text($cocoon_meta_keywords, $target_lang);
            if ($translated_keywords) {
                update_post_meta($new_post_id, 'the_page_meta_keywords', $translated_keywords);
                uzbek_debug_log("Cocoon メタキーワード翻訳完了");
                $translated_count++;
            } else {
                uzbek_debug_log("Cocoon メタキーワード翻訳失敗");
            }
            usleep(200000);
        }
    }
    
    // Yoast SEO対応
    elseif (defined('WPSEO_VERSION')) {
        uzbek_debug_log("Yoast SEOプラグイン対応処理開始");
        
        $meta_title = get_post_meta($original_id, '_yoast_wpseo_title', true);
        $meta_desc = get_post_meta($original_id, '_yoast_wpseo_metadesc', true);
        $meta_keywords = get_post_meta($original_id, '_yoast_wpseo_metakeywords', true);
        $focus_keyword = get_post_meta($original_id, '_yoast_wpseo_focuskw', true);
        
        if (!empty($meta_title)) {
            $translated_title = uzbek_translate_text($meta_title, $target_lang);
            if ($translated_title) {
                update_post_meta($new_post_id, '_yoast_wpseo_title', $translated_title);
                uzbek_debug_log("Yoast SEOタイトル翻訳: " . substr($translated_title, 0, 50));
                $translated_count++;
            }
            usleep(200000);
        }
        
        if (!empty($meta_desc)) {
            $translated_desc = uzbek_translate_text($meta_desc, $target_lang);
            if ($translated_desc) {
                update_post_meta($new_post_id, '_yoast_wpseo_metadesc', $translated_desc);
                uzbek_debug_log("Yoast SEOディスクリプション翻訳完了");
                $translated_count++;
            }
            usleep(200000);
        }
        
        if (!empty($meta_keywords)) {
            $translated_keywords = uzbek_translate_text($meta_keywords, $target_lang);
            if ($translated_keywords) {
                update_post_meta($new_post_id, '_yoast_wpseo_metakeywords', $translated_keywords);
                uzbek_debug_log("Yoast SEOキーワード翻訳完了");
                $translated_count++;
            }
            usleep(200000);
        }
        
        if (!empty($focus_keyword)) {
            $translated_focus = uzbek_translate_text($focus_keyword, $target_lang);
            if ($translated_focus) {
                update_post_meta($new_post_id, '_yoast_wpseo_focuskw', $translated_focus);
                uzbek_debug_log("Yoast フォーカスキーワード翻訳完了");
                $translated_count++;
            }
            usleep(200000);
        }
    }
    
    // All in One SEO対応
    elseif (defined('AIOSEO_VERSION')) {
        uzbek_debug_log("All in One SEO対応処理開始");
        
        $meta_title = get_post_meta($original_id, '_aioseo_title', true);
        $meta_desc = get_post_meta($original_id, '_aioseo_description', true);
        $meta_keywords = get_post_meta($original_id, '_aioseo_keywords', true);
        
        if (!empty($meta_title)) {
            $translated_title = uzbek_translate_text($meta_title, $target_lang);
            if ($translated_title) {
                update_post_meta($new_post_id, '_aioseo_title', $translated_title);
                uzbek_debug_log("AIOSEO タイトル翻訳: " . substr($translated_title, 0, 50));
                $translated_count++;
            }
            usleep(200000);
        }
        
        if (!empty($meta_desc)) {
            $translated_desc = uzbek_translate_text($meta_desc, $target_lang);
            if ($translated_desc) {
                update_post_meta($new_post_id, '_aioseo_description', $translated_desc);
                uzbek_debug_log("AIOSEO ディスクリプション翻訳完了");
                $translated_count++;
            }
            usleep(200000);
        }
        
        if (!empty($meta_keywords)) {
            $translated_keywords = uzbek_translate_text($meta_keywords, $target_lang);
            if ($translated_keywords) {
                update_post_meta($new_post_id, '_aioseo_keywords', $translated_keywords);
                uzbek_debug_log("AIOSEO キーワード翻訳完了");
                $translated_count++;
            }
            usleep(200000);
        }
    }
    
    // SEOPress対応
    elseif (function_exists('seopress_activation')) {
        uzbek_debug_log("SEOPress対応処理開始");
        
        $meta_title = get_post_meta($original_id, '_seopress_titles_title', true);
        $meta_desc = get_post_meta($original_id, '_seopress_titles_desc', true);
        
        if (!empty($meta_title)) {
            $translated_title = uzbek_translate_text($meta_title, $target_lang);
            if ($translated_title) {
                update_post_meta($new_post_id, '_seopress_titles_title', $translated_title);
                uzbek_debug_log("SEOPress タイトル翻訳: " . substr($translated_title, 0, 50));
                $translated_count++;
            }
            usleep(200000);
        }
        
        if (!empty($meta_desc)) {
            $translated_desc = uzbek_translate_text($meta_desc, $target_lang);
            if ($translated_desc) {
                update_post_meta($new_post_id, '_seopress_titles_desc', $translated_desc);
                uzbek_debug_log("SEOPress ディスクリプション翻訳完了");
                $translated_count++;
            }
            usleep(200000);
        }
    }
    
    // 一般的なメタデータ
    else {
        uzbek_debug_log("一般的なSEOメタデータをチェック");
        
        $possible_title_keys = array('seo_title', 'meta_title', '_meta_title');
        $possible_desc_keys = array('seo_description', 'meta_description', '_meta_description', 'description');
        $possible_keyword_keys = array('seo_keywords', 'meta_keywords', '_meta_keywords', 'keywords');
        
        foreach ($possible_title_keys as $key) {
            $meta_title = get_post_meta($original_id, $key, true);
            if (!empty($meta_title)) {
                uzbek_debug_log("一般SEOタイトル発見 ({$key}): " . substr($meta_title, 0, 50));
                $translated_title = uzbek_translate_text($meta_title, $target_lang);
                if ($translated_title) {
                    update_post_meta($new_post_id, $key, $translated_title);
                    uzbek_debug_log("SEOタイトル翻訳完了 ({$key}): " . substr($translated_title, 0, 50));
                    $translated_count++;
                    break;
                }
                usleep(200000);
            }
        }
        
        foreach ($possible_desc_keys as $key) {
            $meta_desc = get_post_meta($original_id, $key, true);
            if (!empty($meta_desc)) {
                uzbek_debug_log("一般SEOディスクリプション発見 ({$key}): " . substr($meta_desc, 0, 50));
                $translated_desc = uzbek_translate_text($meta_desc, $target_lang);
                if ($translated_desc) {
                    update_post_meta($new_post_id, $key, $translated_desc);
                    uzbek_debug_log("SEOディスクリプション翻訳完了 ({$key})");
                    $translated_count++;
                    break;
                }
                usleep(200000);
            }
        }
        
        foreach ($possible_keyword_keys as $key) {
            $meta_keywords = get_post_meta($original_id, $key, true);
            if (!empty($meta_keywords)) {
                uzbek_debug_log("一般SEOキーワード発見 ({$key}): " . substr($meta_keywords, 0, 50));
                $translated_keywords = uzbek_translate_text($meta_keywords, $target_lang);
                if ($translated_keywords) {
                    update_post_meta($new_post_id, $key, $translated_keywords);
                    uzbek_debug_log("SEOキーワード翻訳完了 ({$key})");
                    $translated_count++;
                    break;
                }
                usleep(200000);
            }
        }
    }
    
    if ($translated_count > 0) {
        uzbek_debug_log("SEOメタデータ翻訳完了: {$translated_count}個のメタデータを翻訳");
    } else {
        uzbek_debug_log("SEOメタデータが見つかりません");
    }
    
    uzbek_debug_log("=== SEOメタデータ翻訳終了 ===");
}

function uzbek_create_translation_debug($original_id, $original_post, $lang, $pll_lang) {
    try {
        uzbek_debug_log("タイトル翻訳開始: " . substr($original_post->post_title, 0, 30));
        
        $translated_title = uzbek_translate_text($original_post->post_title, $lang);
        
        if (!$translated_title) {
            uzbek_debug_log("タイトル翻訳失敗");
            return false;
        }
        
        uzbek_debug_log("翻訳されたタイトル: {$translated_title}");
        
        // 本文翻訳
        uzbek_debug_log("本文翻訳開始");
        
        $translated_content = uzbek_translate_text($original_post->post_content, $lang, 'html');
        
        if (!$translated_content) {
            $translated_content = 'Translation failed. / 翻訳に失敗しました。';
            uzbek_debug_log("本文翻訳失敗");
        } else {
            uzbek_debug_log("本文翻訳成功");
        }
        
        $new_post_id = wp_insert_post(array(
            'post_title' => $translated_title,
            'post_content' => $translated_content,
            'post_status' => 'publish',
            'post_type' => $original_post->post_type,
            'post_author' => $original_post->post_author
        ));
        
        if (is_wp_error($new_post_id)) {
            uzbek_debug_log("投稿作成エラー: " . $new_post_id->get_error_message());
            return false;
        }
        
        if ($new_post_id > 0) {
            uzbek_debug_log("新{$original_post->post_type}作成成功: ID {$new_post_id}");
            
            if (function_exists('pll_set_post_language')) {
                pll_set_post_language($new_post_id, $pll_lang);
                uzbek_debug_log("言語設定完了: {$pll_lang}");
            }
            
            uzbek_translate_and_set_categories($original_id, $new_post_id, $lang, $pll_lang);
            uzbek_translate_and_set_tags($original_id, $new_post_id, $lang, $pll_lang);
            uzbek_translate_and_set_seo_meta($original_id, $new_post_id, $lang);
            
            $thumbnail_id = get_post_thumbnail_id($original_id);

            if (!$thumbnail_id) {
                $thumbnail_id = get_post_meta($original_id, '_thumbnail_id', true);
                uzbek_debug_log("直接メタから取得試行: " . ($thumbnail_id ? $thumbnail_id : 'なし'));
            }

            if ($thumbnail_id) {
                $set_result = set_post_thumbnail($new_post_id, $thumbnail_id);
                if ($set_result) {
                    uzbek_debug_log("アイキャッチ画像コピー完了: ID {$thumbnail_id}");
                } else {
                    uzbek_debug_log("アイキャッチ画像設定失敗: ID {$thumbnail_id}");
                }
            } else {
                uzbek_debug_log("元投稿にアイキャッチ画像なし");
            }
            
            return $new_post_id;
        }
        
        return false;
        
    } catch (Exception $e) {
        uzbek_debug_log("翻訳作成例外: " . $e->getMessage());
        return false;
    }
}

// フック設定
add_action('save_post', 'uzbek_immediate_auto_translate', 20, 3);

// ===== Google Apps Script用 カスタムエンドポイント =====
add_action('rest_api_init', function() {
    register_rest_route('custom/v1', '/update-seo', array(
        'methods' => 'POST',
        'callback' => 'update_post_seo_fields',
        'permission_callback' => function() {
            return current_user_can('edit_posts');
        }
    ));
});

function update_post_seo_fields($request) {
    $post_id = $request->get_param('post_id');
    $seo_title = $request->get_param('seo_title');
    $meta_description = $request->get_param('meta_description');
    $meta_keywords = $request->get_param('meta_keywords');
    
    if($seo_title) update_post_meta($post_id, 'the_page_seo_title', $seo_title);
    if($meta_description) update_post_meta($post_id, 'the_page_meta_description', $meta_description);
    if($meta_keywords) update_post_meta($post_id, 'the_page_meta_keywords', $meta_keywords);
    
    return array(
        'success' => true,
        'post_id' => $post_id,
        'seo_title' => $seo_title,
        'meta_description' => $meta_description,
        'meta_keywords' => $meta_keywords
    );
}


/**
 * ============================================================
 * M&Aポータル - DDチェックリスト完全版
 * 全33項目のデューデリジェンス対応
 * ============================================================
 */

// ============================================================
// 基本設定
// ============================================================

function ma_company_register_post_type() {
    if (post_type_exists('ma_company')) return;
    register_post_type('ma_company', array(
        'labels' => array('name' => 'M&A企業情報'),
        'public' => true,
        'has_archive' => true,
        'menu_icon' => 'dashicons-building',
        'supports' => array('title', 'editor', 'thumbnail', 'comments'),
        'show_in_rest' => true,
    ));
}
add_action('init', 'ma_company_register_post_type');

function ma_industry_register_taxonomy() {
    if (taxonomy_exists('ma_industry')) return;
    register_taxonomy('ma_industry', array('ma_company'), array(
        'hierarchical' => true,
        'labels' => array('name' => '業種'),
        'show_in_rest' => true,
    ));
}
add_action('init', 'ma_industry_register_taxonomy');

// ============================================================
// Phase 24: DDカスタムフィールド定義
// ============================================================

function ma_dd_fields() {
    return array(
        'financial' => array(
            'label' => '📈 経営・財務',
            'fields' => array(
                'audit_firm' => array('label' => '監査法人名', 'type' => 'text'),
                'audit_opinion' => array('label' => '監査意見の種類', 'type' => 'select', 'options' => array('無限定適正', '限定付適正', '不適正', '意見不表明')),
                'off_balance_debt' => array('label' => '簿外債務', 'type' => 'textarea'),
                'tax_risk' => array('label' => '税務リスク', 'type' => 'textarea'),
                'cashflow_details' => array('label' => 'キャッシュフロー詳細', 'type' => 'textarea'),
                'budget_accuracy' => array('label' => '予算管理精度', 'type' => 'select', 'options' => array('高', '中', '低')),
                'creditors' => array('label' => '主要債権者・債務者', 'type' => 'textarea'),
                'internal_control' => array('label' => '内部統制整備状況', 'type' => 'select', 'options' => array('整備済', '一部整備', '未整備')),
            )
        ),
        'ma' => array(
            'label' => '🤝 M&A・取引',
            'fields' => array(
                'ma_purpose' => array('label' => 'M&A目的', 'type' => 'textarea'),
                'management_involvement' => array('label' => '希望経営関与レベル', 'type' => 'select', 'options' => array('完全統合', '部分関与', '独立維持')),
                'price_range' => array('label' => '想定買収価格範囲', 'type' => 'text'),
                'past_ma' => array('label' => '過去のM&A経験', 'type' => 'textarea'),
                'key_suppliers' => array('label' => '主要サプライヤー', 'type' => 'textarea'),
                'swot_analysis' => array('label' => 'SWOT分析', 'type' => 'textarea'),
                'bcp' => array('label' => '事業継続計画(BCP)', 'type' => 'select', 'options' => array('あり', 'なし')),
            )
        ),
        'legal' => array(
            'label' => '⚖️ 法務・規制',
            'fields' => array(
                'licenses' => array('label' => '事業ライセンス・許認可', 'type' => 'textarea'),
                'litigation' => array('label' => '訴訟・係争履歴', 'type' => 'textarea'),
                'ip_rights' => array('label' => '知的財産権', 'type' => 'textarea'),
                'land_rights' => array('label' => '土地・不動産権利', 'type' => 'textarea'),
                'foreign_investment' => array('label' => '外国投資規制', 'type' => 'textarea'),
                'antitrust' => array('label' => '独占禁止法対応', 'type' => 'select', 'options' => array('不要', '事前届出済', '未対応')),
                'labor_risk' => array('label' => '雇用・労働リスク', 'type' => 'textarea'),
            )
        ),
        'social' => array(
            'label' => '🌍 社会・環境',
            'fields' => array(
                'turnover_rate' => array('label' => '離職率（%）', 'type' => 'number'),
                'employee_composition' => array('label' => '従業員構成', 'type' => 'textarea'),
                'labor_union' => array('label' => '労働組合', 'type' => 'select', 'options' => array('あり', 'なし')),
                'corporate_culture' => array('label' => '企業文化・経営陣特徴', 'type' => 'textarea'),
                'csr_activities' => array('label' => 'CSR活動', 'type' => 'textarea'),
                'environmental' => array('label' => '環境への取り組み', 'type' => 'textarea'),
            )
        ),
        'tech' => array(
            'label' => '💡 技術・資産',
            'fields' => array(
                'tech_uniqueness' => array('label' => '技術の独自性', 'type' => 'textarea'),
                'rd_investment' => array('label' => 'R&D投資額', 'type' => 'text'),
                'it_systems' => array('label' => 'ITシステム構成', 'type' => 'textarea'),
                'equipment_age' => array('label' => '設備稼働年数', 'type' => 'text'),
                'inventory_mgmt' => array('label' => '在庫管理方法', 'type' => 'textarea'),
            )
        ),
    );
}

// ============================================================
// 管理画面: DDメタボックス追加
// ============================================================

function ma_add_dd_metaboxes() {
    $dd_categories = ma_dd_fields();
    
    foreach ($dd_categories as $cat_key => $cat_data) {
        add_meta_box(
            'ma_dd_' . $cat_key,
            $cat_data['label'],
            'ma_dd_metabox_callback',
            'ma_company',
            'normal',
            'high',
            array('category' => $cat_key, 'fields' => $cat_data['fields'])
        );
    }
}
add_action('add_meta_boxes', 'ma_add_dd_metaboxes');

function ma_dd_metabox_callback($post, $metabox) {
    $category = $metabox['args']['category'];
    $fields = $metabox['args']['fields'];
    
    wp_nonce_field('ma_dd_save', 'ma_dd_nonce');
    
    echo '<table class="form-table">';
    foreach ($fields as $field_key => $field_data) {
        $full_key = 'dd_' . $category . '_' . $field_key;
        $value = get_post_meta($post->ID, $full_key, true);
        
        echo '<tr>';
        echo '<th><label for="' . $full_key . '">' . $field_data['label'] . '</label></th>';
        echo '<td>';
        
        switch ($field_data['type']) {
            case 'textarea':
                echo '<textarea id="' . $full_key . '" name="' . $full_key . '" rows="4" style="width:100%;">' . esc_textarea($value) . '</textarea>';
                break;
            case 'select':
                echo '<select id="' . $full_key . '" name="' . $full_key . '" style="width:100%;">';
                echo '<option value="">選択してください</option>';
                foreach ($field_data['options'] as $opt) {
                    echo '<option value="' . esc_attr($opt) . '"' . selected($value, $opt, false) . '>' . esc_html($opt) . '</option>';
                }
                echo '</select>';
                break;
            case 'number':
                echo '<input type="number" id="' . $full_key . '" name="' . $full_key . '" value="' . esc_attr($value) . '" style="width:100%;">';
                break;
            default:
                echo '<input type="text" id="' . $full_key . '" name="' . $full_key . '" value="' . esc_attr($value) . '" style="width:100%;">';
        }
        
        echo '</td>';
        echo '</tr>';
    }
    echo '</table>';
}

function ma_save_dd_metaboxes($post_id) {
    if (!isset($_POST['ma_dd_nonce']) || !wp_verify_nonce($_POST['ma_dd_nonce'], 'ma_dd_save')) return;
    if (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) return;
    if (!current_user_can('edit_post', $post_id)) return;
    
    $dd_fields = ma_dd_fields();
    
    foreach ($dd_fields as $cat_key => $cat_data) {
        foreach ($cat_data['fields'] as $field_key => $field_data) {
            $full_key = 'dd_' . $cat_key . '_' . $field_key;
            if (isset($_POST[$full_key])) {
                update_post_meta($post_id, $full_key, sanitize_text_field($_POST[$full_key]));
            }
        }
    }
}
add_action('save_post', 'ma_save_dd_metaboxes');

// ============================================================
// フロントエンド: DD検索フォーム（拡張版）
// ============================================================

function ma_search_form_shortcode() {
    $industries = get_terms(array('taxonomy' => 'ma_industry', 'hide_empty' => false));
    ob_start();
    ?>
    <div class="ma-search-container">
        <form method="GET" action="<?php echo esc_url(home_url('/ma-search-results/')); ?>">
            <h3>基本検索</h3>
            <input type="text" name="keyword" placeholder="企業名" value="<?php echo esc_attr($_GET['keyword'] ?? ''); ?>">
            <select name="industry">
                <option value="">すべての業種</option>
                <?php foreach ($industries as $ind): ?>
                    <option value="<?php echo esc_attr($ind->slug); ?>" <?php selected($_GET['industry'] ?? '', $ind->slug); ?>><?php echo esc_html($ind->name); ?></option>
                <?php endforeach; ?>
            </select>
            
            <h3>📈 財務DD</h3>
            <select name="audit_opinion">
                <option value="">監査意見（すべて）</option>
                <option value="無限定適正" <?php selected($_GET['audit_opinion'] ?? '', '無限定適正'); ?>>無限定適正</option>
                <option value="限定付適正" <?php selected($_GET['audit_opinion'] ?? '', '限定付適正'); ?>>限定付適正</option>
            </select>
            
            <select name="internal_control">
                <option value="">内部統制（すべて）</option>
                <option value="整備済" <?php selected($_GET['internal_control'] ?? '', '整備済'); ?>>整備済</option>
                <option value="一部整備" <?php selected($_GET['internal_control'] ?? '', '一部整備'); ?>>一部整備</option>
            </select>
            
            <h3>⚖️ 法務DD</h3>
            <select name="bcp">
                <option value="">BCP（すべて）</option>
                <option value="あり" <?php selected($_GET['bcp'] ?? '', 'あり'); ?>>あり</option>
                <option value="なし" <?php selected($_GET['bcp'] ?? '', 'なし'); ?>>なし</option>
            </select>
            
            <select name="labor_union">
                <option value="">労働組合（すべて）</option>
                <option value="あり" <?php selected($_GET['labor_union'] ?? '', 'あり'); ?>>あり</option>
                <option value="なし" <?php selected($_GET['labor_union'] ?? '', 'なし'); ?>>なし</option>
            </select>
            
            <button type="submit" class="ma-btn">DD検索</button>
        </form>
    </div>
    
    <style>
    .ma-search-container { max-width: 800px; margin: 20px auto; padding: 30px; background: #f9f9f9; border-radius: 8px; }
    .ma-search-container h3 { margin-top: 20px; color: #333; border-bottom: 2px solid #0073aa; padding-bottom: 5px; }
    input, select { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; }
    .ma-btn { width: 100%; padding: 15px; background: #0073aa; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; margin-top: 20px; }
    </style>
    <?php
    return ob_get_clean();
}
add_shortcode('ma_search_form', 'ma_search_form_shortcode');

// ============================================================
// フロントエンド: DD検索結果（完了度表示）
// ============================================================

function ma_search_results_shortcode() {
    // パラメータ取得
    $keyword = sanitize_text_field($_GET['keyword'] ?? '');
    $industry = sanitize_text_field($_GET['industry'] ?? '');
    $audit_opinion = sanitize_text_field($_GET['audit_opinion'] ?? '');
    $internal_control = sanitize_text_field($_GET['internal_control'] ?? '');
    $bcp = sanitize_text_field($_GET['bcp'] ?? '');
    $labor_union = sanitize_text_field($_GET['labor_union'] ?? '');
    
    $args = array('post_type' => 'ma_company', 'posts_per_page' => -1);
    
    if ($keyword) $args['s'] = $keyword;
    if ($industry) $args['tax_query'] = array(array('taxonomy' => 'ma_industry', 'field' => 'slug', 'terms' => $industry));
    
    // メタクエリでDDフィルター
    $meta_query = array('relation' => 'AND');
    if ($audit_opinion) $meta_query[] = array('key' => 'dd_financial_audit_opinion', 'value' => $audit_opinion, 'compare' => '=');
    if ($internal_control) $meta_query[] = array('key' => 'dd_financial_internal_control', 'value' => $internal_control, 'compare' => '=');
    if ($bcp) $meta_query[] = array('key' => 'dd_ma_bcp', 'value' => $bcp, 'compare' => '=');
    if ($labor_union) $meta_query[] = array('key' => 'dd_social_labor_union', 'value' => $labor_union, 'compare' => '=');
    
    if (count($meta_query) > 1) $args['meta_query'] = $meta_query;
    
    $query = new WP_Query($args);
    
    ob_start();
    ?>
    <div class="ma-results-container">
        <div class="ma-toolbar">
            <div>検索結果: <strong><?php echo $query->found_posts; ?></strong>件</div>
            <button onclick="ma_export_dd_csv()" class="ma-btn-export">DD情報エクスポート</button>
        </div>
        
        <div class="ma-results">
            <?php while ($query->have_posts()): $query->the_post(); 
                $company_id = get_the_ID();
                
                // DD完了度計算
                $dd_fields = ma_dd_fields();
                $total_fields = 0;
                $filled_fields = 0;
                
                foreach ($dd_fields as $cat_key => $cat_data) {
                    foreach ($cat_data['fields'] as $field_key => $field_data) {
                        $total_fields++;
                        $value = get_post_meta($company_id, 'dd_' . $cat_key . '_' . $field_key, true);
                        if (!empty($value)) $filled_fields++;
                    }
                }
                
                $completion = $total_fields > 0 ? round(($filled_fields / $total_fields) * 100) : 0;
            ?>
                <div class="ma-card">
                    <h3><?php the_title(); ?></h3>
                    
                    <!-- DD完了度 -->
                    <div class="ma-dd-progress">
                        <div class="ma-progress-label">DD完了度: <?php echo $completion; ?>%</div>
                        <div class="ma-progress-bar">
                            <div class="ma-progress-fill" style="width: <?php echo $completion; ?>%;"></div>
                        </div>
                        <div class="ma-progress-detail"><?php echo $filled_fields; ?>/<?php echo $total_fields; ?> 項目入力済</div>
                    </div>
                    
                    <!-- 基本情報 -->
                    <p><strong>設立:</strong> <?php echo get_post_meta($company_id, 'founded_year', true); ?>年</p>
                    <p><strong>従業員:</strong> <?php echo get_post_meta($company_id, 'employees', true); ?>名</p>
                    
                    <!-- DD主要項目 -->
                    <?php
                    $audit = get_post_meta($company_id, 'dd_financial_audit_opinion', true);
                    $bcp_val = get_post_meta($company_id, 'dd_ma_bcp', true);
                    ?>
                    <?php if ($audit): ?><span class="ma-badge">監査: <?php echo esc_html($audit); ?></span><?php endif; ?>
                    <?php if ($bcp_val): ?><span class="ma-badge">BCP: <?php echo esc_html($bcp_val); ?></span><?php endif; ?>
                    
                    <div class="ma-card-actions">
                        <a href="<?php the_permalink(); ?>" class="ma-btn-small">DD詳細</a>
                        <button onclick="ma_dd_export(<?php echo $company_id; ?>)" class="ma-btn-small">PDFエクスポート</button>
                    </div>
                </div>
            <?php endwhile; wp_reset_postdata(); ?>
        </div>
    </div>
    
    <style>
    .ma-results-container { max-width: 1200px; margin: 20px auto; }
    .ma-toolbar { display: flex; justify-content: space-between; padding: 15px; background: #f9f9f9; margin-bottom: 20px; }
    .ma-btn-export { padding: 10px 20px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; }
    .ma-card { background: white; padding: 25px; margin: 15px 0; border: 1px solid #ddd; border-radius: 8px; }
    .ma-dd-progress { margin: 15px 0; padding: 15px; background: #f0f0f0; border-radius: 5px; }
    .ma-progress-label { font-weight: bold; margin-bottom: 5px; }
    .ma-progress-bar { width: 100%; height: 20px; background: #ddd; border-radius: 10px; overflow: hidden; }
    .ma-progress-fill { height: 100%; background: linear-gradient(90deg, #0073aa, #00a0d2); transition: width 0.3s; }
    .ma-progress-detail { font-size: 12px; color: #666; margin-top: 5px; }
    .ma-badge { display: inline-block; padding: 5px 10px; margin: 5px 5px 0 0; background: #e3f2fd; border-radius: 3px; font-size: 12px; }
    .ma-card-actions { margin-top: 15px; display: flex; gap: 10px; }
    .ma-btn-small { padding: 8px 16px; background: #0073aa; color: white; text-decoration: none; border-radius: 4px; border: none; cursor: pointer; }
    </style>
    
    <script>
    function ma_export_dd_csv() {
        window.location.href = '<?php echo admin_url('admin-ajax.php'); ?>?action=ma_export_dd_csv';
    }
    
    function ma_dd_export(companyId) {
        window.location.href = '<?php echo admin_url('admin-ajax.php'); ?>?action=ma_dd_pdf&company_id=' + companyId;
    }
    </script>
    <?php
    return ob_get_clean();
}
add_shortcode('ma_search_results', 'ma_search_results_shortcode');

// ============================================================
// 単一企業ページ: DD完全表示
// ============================================================

function ma_dd_details_shortcode() {
    if (!is_singular('ma_company')) return '';
    
    $company_id = get_the_ID();
    $dd_categories = ma_dd_fields();
    
    ob_start();
    ?>
    <div class="ma-dd-details">
        <h2>デューデリジェンス情報</h2>
        
        <?php foreach ($dd_categories as $cat_key => $cat_data): ?>
            <div class="ma-dd-category">
                <h3><?php echo $cat_data['label']; ?></h3>
                <table class="ma-dd-table">
                    <?php foreach ($cat_data['fields'] as $field_key => $field_data): 
                        $value = get_post_meta($company_id, 'dd_' . $cat_key . '_' . $field_key, true);
                    ?>
                        <tr>
                            <th><?php echo $field_data['label']; ?></th>
                            <td><?php echo $value ? esc_html($value) : '<span class="ma-empty">未入力</span>'; ?></td>
                        </tr>
                    <?php endforeach; ?>
                </table>
            </div>
        <?php endforeach; ?>
        
        <button onclick="ma_dd_export(<?php echo $company_id; ?>)" class="ma-btn">PDF出力</button>
    </div>
    
    <style>
    .ma-dd-details { max-width: 1000px; margin: 30px auto; padding: 30px; background: white; border: 1px solid #ddd; border-radius: 8px; }
    .ma-dd-category { margin: 30px 0; }
    .ma-dd-category h3 { padding: 10px; background: #0073aa; color: white; border-radius: 4px; }
    .ma-dd-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    .ma-dd-table th { width: 30%; padding: 12px; background: #f9f9f9; border: 1px solid #ddd; font-weight: bold; text-align: left; }
    .ma-dd-table td { padding: 12px; border: 1px solid #ddd; }
    .ma-empty { color: #999; font-style: italic; }
    .ma-btn { padding: 15px 30px; background: #0073aa; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; margin-top: 20px; }
    </style>
    <?php
    return ob_get_clean();
}
add_shortcode('ma_dd_details', 'ma_dd_details_shortcode');

// ============================================================
// AJAX: CSV/PDFエクスポート
// ============================================================

function ma_ajax_export_dd_csv() {
    header('Content-Type: text/csv; charset=utf-8');
    header('Content-Disposition: attachment; filename=dd-export-' . date('Ymd') . '.csv');
    
    $output = fopen('php://output', 'w');
    
    // ヘッダー
    $headers = array('企業名', '業種', 'DD完了度(%)');
    $dd_fields = ma_dd_fields();
    foreach ($dd_fields as $cat_data) {
        foreach ($cat_data['fields'] as $field_data) {
            $headers[] = $field_data['label'];
        }
    }
    fputcsv($output, $headers);
    
    // データ
    $companies = get_posts(array('post_type' => 'ma_company', 'posts_per_page' => -1));
    foreach ($companies as $company) {
        $row = array($company->post_title, '', '');
        
        foreach ($dd_fields as $cat_key => $cat_data) {
            foreach ($cat_data['fields'] as $field_key => $field_data) {
                $value = get_post_meta($company->ID, 'dd_' . $cat_key . '_' . $field_key, true);
                $row[] = $value;
            }
        }
        
        fputcsv($output, $row);
    }
    
    fclose($output);
    exit;
}
add_action('wp_ajax_ma_export_dd_csv', 'ma_ajax_export_dd_csv');
add_action('wp_ajax_nopriv_ma_export_dd_csv', 'ma_ajax_export_dd_csv');

function ma_ajax_dd_pdf() {
    $company_id = intval($_GET['company_id']);
    // PDF生成ライブラリ（TCPDF等）を使用して実装
    // ここでは簡易的にHTMLで出力
    
    header('Content-Type: text/html; charset=utf-8');
    echo '<h1>' . get_the_title($company_id) . ' - DD Report</h1>';
    echo '<p>DD情報をここに出力...</p>';
    exit;
}
add_action('wp_ajax_ma_dd_pdf', 'ma_ajax_dd_pdf');
add_action('wp_ajax_nopriv_ma_dd_pdf', 'ma_ajax_dd_pdf');