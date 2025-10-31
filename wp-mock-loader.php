<?php
/**
 * モックWordPressローダー - 修正版
 * データベース不要の開発環境用
 */

// ABSPATHを最初に定義
if (!defined('ABSPATH')) {
    define('ABSPATH', __DIR__ . '/');
}

// モックWordPress環境
class MockWordPress {
    public function __construct() {
        $this->define_mock_constants();
        $this->define_mock_functions();
        echo "✅ モックWordPress環境を読み込みました\n";
    }
    
    private function define_mock_constants() {
        // 必要なWordPress定数を定義
        $constants = [
            'WP_DEBUG' => false,
            'WPINC' => 'wp-includes',
            'WP_CONTENT_DIR' => ABSPATH . 'wp-content',
            'WP_PLUGIN_DIR' => ABSPATH . 'wp-content/plugins',
            'WPLANG' => '',
            'WP_POST_REVISIONS' => false
        ];
        
        foreach ($constants as $constant => $value) {
            if (!defined($constant)) {
                define($constant, $value);
            }
        }
    }
    
    private function define_mock_functions() {
        // 基本的なWordPress関数のモック
        
        if (!function_exists('add_action')) {
            function add_action($hook, $callback, $priority = 10, $accepted_args = 1) {
                // モック: 何もしない
                return true;
            }
        }
        
        if (!function_exists('add_filter')) {
            function add_filter($hook, $callback, $priority = 10, $accepted_args = 1) {
                // モック: コールバックを返す
                return $callback;
            }
        }
        
        if (!function_exists('wp_insert_post')) {
            function wp_insert_post($postarr, $wp_error = false) {
                // モック: ダミーの投稿IDを返す
                return rand(1, 1000);
            }
        }
        
        if (!function_exists('wp_set_object_terms')) {
            function wp_set_object_terms($object_id, $terms, $taxonomy, $append = false) {
                // モック: 成功を返す
                return true;
            }
        }
        
        if (!function_exists('get_terms')) {
            function get_terms($args = array()) {
                // モック: 空の配列を返す
                return array();
            }
        }
        
        if (!function_exists('taxonomy_exists')) {
            function taxonomy_exists($taxonomy) {
                // モック: 常にtrueを返す
                return true;
            }
        }
        
        if (!function_exists('register_taxonomy')) {
            function register_taxonomy($taxonomy, $object_type, $args = array()) {
                // モック: 成功を返す
                return true;
            }
        }
    }
}

// メインのwp-load.phpを試す前にモックを準備
$mock_loaded = false;

// メインのwp-load.phpを試す
if (file_exists(ABSPATH . 'wp-load.php')) {
    try {
        // データベースエラーを抑制
        @require_once ABSPATH . 'wp-load.php';
        
        // 正常に読み込めたかチェック
        if (function_exists('add_action')) {
            echo "✅ 本物のWordPressを読み込みました\n";
        } else {
            throw new Exception("WordPress関数が利用できません");
        }
    } catch (Exception $e) {
        echo "⚠️ 本物のWordPress読み込みに失敗: " . $e->getMessage() . "\n";
        echo "🔧 モックWordPressにフォールバックします\n";
        new MockWordPress();
        $mock_loaded = true;
    }
} else {
    echo "🔧 モックWordPressを使用します\n";
    new MockWordPress();
    $mock_loaded = true;
}

// モックが読み込まれたことを確認
if ($mock_loaded && !function_exists('add_action')) {
    // フォールバックとして直接関数を定義
    if (!function_exists('add_action')) {
        function add_action($hook, $callback, $priority = 10, $accepted_args = 1) {
            return true;
        }
    }
}
?>
