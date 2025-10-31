<?php
/**
 * Plugin Name: Auto Deploy Receiver
 * Description: Codespaceからの自動デプロイを受け取る
 * Version: 1.0.0
 * Author: Auto Deploy System
 */

add_action('rest_api_init', function() {
    register_rest_route('custom/v1', '/deploy-functions', array(
        'methods' => 'POST',
        'callback' => 'handle_functions_deploy',
        'permission_callback' => function() {
            return current_user_can('manage_options');
        }
    ));
    
    register_rest_route('custom/v1', '/flush-rewrite', array(
        'methods' => 'POST',
        'callback' => 'handle_flush_rewrite',
        'permission_callback' => function() {
            return current_user_can('manage_options');
        }
    ));
});

function handle_functions_deploy($request) {
    $file_content = $request->get_param('file_content');
    
    if (empty($file_content)) {
        return new WP_Error('empty_content', 'ファイル内容が空です', array('status' => 400));
    }
    
    $theme_dir = get_stylesheet_directory();
    $functions_path = $theme_dir . '/functions.php';
    
    $backup_path = $functions_path . '.backup.' . date('YmdHis');
    if (file_exists($functions_path)) {
        copy($functions_path, $backup_path);
    }
    
    $result = file_put_contents($functions_path, $file_content);
    
    if ($result === false) {
        return new WP_Error('write_failed', 'ファイル書き込み失敗', array('status' => 500));
    }
    
    if (function_exists('opcache_reset')) {
        opcache_reset();
    }
    
    return array(
        'success' => true,
        'message' => 'デプロイ成功',
        'backup' => $backup_path,
        'bytes_written' => $result
    );
}

function handle_flush_rewrite($request) {
    flush_rewrite_rules();
    
    return array(
        'success' => true,
        'message' => 'パーマリンク更新完了'
    );
}
