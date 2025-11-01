<?php
/**
 * ACFフィールドグループ登録コード
 * このコードをfunctions.phpに追加すると、ACF GUIなしでフィールドを登録できます
 */

if( function_exists('acf_add_local_field_group') ):

acf_add_local_field_group(array(
    'key' => 'group_ma_company_details',
    'title' => '企業詳細情報',
    'fields' => array(
        array(
            'key' => 'field_location',
            'label' => '所在地',
            'name' => 'location',
            'type' => 'text',
            'required' => 1,
            'placeholder' => '例: 東京都渋谷区',
        ),
        array(
            'key' => 'field_capital',
            'label' => '資本金（万円）',
            'name' => 'capital',
            'type' => 'number',
            'required' => 1,
            'placeholder' => '例: 10000',
            'min' => 0,
        ),
        array(
            'key' => 'field_employees',
            'label' => '従業員数',
            'name' => 'employees',
            'type' => 'number',
            'required' => 1,
            'placeholder' => '例: 50',
            'min' => 0,
        ),
        array(
            'key' => 'field_revenue',
            'label' => '年商（万円）',
            'name' => 'revenue',
            'type' => 'number',
            'required' => 1,
            'placeholder' => '例: 100000',
            'min' => 0,
        ),
        array(
            'key' => 'field_deal_type',
            'label' => '希望条件',
            'name' => 'deal_type',
            'type' => 'select',
            'required' => 1,
            'choices' => array('売却希望' => '売却希望', '買収希望' => '買収希望'),
        ),
    ),
    'location' => array(
        array(
            array(
                'param' => 'post_type',
                'operator' => '==',
                'value' => 'ma_company',
            ),
        ),
    ),
    'position' => 'normal',
    'style' => 'default',
));

endif;
