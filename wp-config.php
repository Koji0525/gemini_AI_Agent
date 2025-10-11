<?php
/**
 * The base configuration for WordPress
 *
 * The wp-config.php creation script uses this file during the installation.
 * You don't have to use the website, you can copy this file to "wp-config.php"
 * and fill in the values.
 *
 * This file contains the following configurations:
 *
 * * Database settings
 * * Secret keys
 * * Database table prefix
 * * ABSPATH
 *
 * @link https://developer.wordpress.org/advanced-administration/wordpress/wp-config/
 *
 * @package WordPress
 */

// ** Database settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define( 'DB_NAME', 'xs395696_wp4' );

/** Database username */
define( 'DB_USER', 'xs395696_wp4' );

/** Database password */
define( 'DB_PASSWORD', '45gbczemf7' );

/** Database hostname */
define( 'DB_HOST', 'mysql10051.xserver.jp' );

/** Database charset to use in creating database tables. */
define( 'DB_CHARSET', 'utf8' );

/** The database collate type. Don't change this if in doubt. */
define( 'DB_COLLATE', '' );

/**#@+
 * Authentication unique keys and salts.
 *
 * Change these to different unique phrases! You can generate these using
 * the {@link https://api.wordpress.org/secret-key/1.1/salt/ WordPress.org secret-key service}.
 *
 * You can change these at any point in time to invalidate all existing cookies.
 * This will force all users to have to log in again.
 *
 * @since 2.6.0
 */
define( 'AUTH_KEY',         '8>~(37LYD; }bOIM(:SqGq^|DgYJ{LM*`)~@$6wppD%+;t u:M7WcRbfu$bXBva.' );
define( 'SECURE_AUTH_KEY',  '>Z3]cPkq_,u(:xlW-l3[U,7S2np_KGeKsIDHJqF ?fL]k[r/bhmRDw66sR.d^.RA' );
define( 'LOGGED_IN_KEY',    ' z^R!T)#k7sm|/K}Hg>t2,y6Ki[MV+_mx@{9DY@06t*<*nmj<^GE{p^3K;r#&bW&' );
define( 'NONCE_KEY',        '#{~.~vw$}[wQdp]QR=PXvy?DQ:BgS*;<[{aTEVew5Dg&oeEy {[=J q-w2htH0x:' );
define( 'AUTH_SALT',        'p/ W0Ulvp=KzG~JhBcVpo5!g=LVaoHYIW&8Iv}<w`MjL+>e`=!C-u&i`._& ?igT' );
define( 'SECURE_AUTH_SALT', '^cP&<Ekj|.6_U@W# *HF3(D$OJR}[@[t4A%5ZX;*csi]yaPh8^(tr=4Qv<G/<S,X' );
define( 'LOGGED_IN_SALT',   'b$Fe9K yS?>kQD+[|*vKv37}-d;j#>gP#ntL33B`7~C><Fm0|ny,`@(5I9a&=1>#' );
define( 'NONCE_SALT',       'p6Tqsi5Mjtt-7jZ~xx~?x3U,BSFmf=Gq</rL~&6MYJT#D_bjm-m9w[>:~:l<x/q&' );

/**#@-*/

/**
 * WordPress database table prefix.
 *
 * You can have multiple installations in one database if you give each
 * a unique prefix. Only numbers, letters, and underscores please!
 *
 * At the installation time, database tables are created with the specified prefix.
 * Changing this value after WordPress is installed will make your site think
 * it has not been installed.
 *
 * @link https://developer.wordpress.org/advanced-administration/wordpress/wp-config/#table-prefix
 */
$table_prefix = 'wp_';

/**
 * For developers: WordPress debugging mode.
 *
 * Change this to true to enable the display of notices during development.
 * It is strongly recommended that plugin and theme developers use WP_DEBUG
 * in their development environments.
 *
 * For information on other constants that can be used for debugging,
 * visit the documentation.
 *
 * @link https://developer.wordpress.org/advanced-administration/debug/debug-wordpress/
 */
define( 'WP_DEBUG', false );

/* Add any custom values between this line and the "stop editing" line. */



/* That's all, stop editing! Happy publishing. */

/** Absolute path to the WordPress directory. */
if ( ! defined( 'ABSPATH' ) ) {
	define( 'ABSPATH', __DIR__ . '/' );
}

/** Sets up WordPress vars and included files. */
require_once ABSPATH . 'wp-settings.php';
