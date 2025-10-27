
<?php
// POCデモ用カスタム投稿タイプ
function poc_register_company_post_type() {
    $args = array(
        'public' => true,
        'label'  => 'Companies',
        'supports' => array('title', 'editor', 'custom-fields'),
        'has_archive' => true,
    );
    register_post_type('company', $args);
}
add_action('init', 'poc_register_company_post_type');
?>
            