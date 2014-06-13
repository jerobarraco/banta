package com.moongate.bantatc;
import android.app.Activity;
import android.content.SharedPreferences;
import android.content.res.Resources;
import android.util.Log;
import java.io.UnsupportedEncodingException;
import java.security.MessageDigest;

/**
 *
 * @author MoonGate
 */
public class Pref {
	//Puede acceder a estas variables desde otros lados
	//Y se guardan al cerrar la app. 
	//Hay que tratar de modificarlas solo en el main thread o en el main_activity
	public static String ip;
	public static String user;
	public static String pwd;
	public static String port;
	public static final String PREFS_NAME = "com.moongate.bantatc.pref";
	//cacheamos la autenticacion aca para evitar recalcularla en cada request.
	public static String encAuth;
	
	public static void cargar(Activity parent){
		//La idea es llamar esta funcion solamente desde el mainActivity (al igual que guardar)
		
		//Obtenemos los valores por default en caso que sea la primera vez que se ejecutó (o se borraron los settings)
		Resources res = parent.getResources();
		
		String default_ip = res.getString(R.string.default_ip);
		String default_port = res.getString(R.string.default_port);
		String default_user = res.getString(R.string.default_user);
		String default_pwd = res.getString(R.string.default_password);
		
		//creamos el editor de settings
		SharedPreferences settings = parent.getSharedPreferences(PREFS_NAME, 0);
		
		//le pedimos la ip (si no la encunetra nos da la default
		ip = settings.getString("ip", default_ip);
		port = settings.getString("port", default_port);
		user = settings.getString("user", default_user);
		pwd = settings.getString("pwd", default_pwd);
		reencode();
	}
	public static void guardar(Activity parent){
		//Esta funcion la llama el mainactivity cuando se termina la app (cosa que con el cache de android no pasa seguido)
		// We need an Editor object to make preference changes.
		// All objects are from android.context.Context
		SharedPreferences settings = parent.getSharedPreferences(PREFS_NAME, 0);
		SharedPreferences.Editor editor = settings.edit();
		editor.putString("ip", ip);
		editor.putString("port", port);
		editor.putString("user", user);
		editor.putString("pwd", pwd);
		// Commit the edits!
		editor.commit();
	}
	public static void reencode(){
		//El usuario puede llegar a cambiar el password en el medio de la app. 
		//asi que hay que hacer esto cada vez que se cambia el password, asi cacheamos la variable
		//encAuth para los ws
		encAuth = genEncAuth(user, pwd);
	}
	public static String encodePassword(String password){
		String encoded = "";
		try{
			//sha es una encripción rápida (un hash), una verdadera encripcion sería AES o BlowFish,
			//pero las implementaciones en android son demasiado complicadas y no vale la pena
			MessageDigest digester = MessageDigest.getInstance("sha1");
			encoded = hexString(digester.digest(password.getBytes("UTF-8")));
		}
		catch (Exception  e){
			Log.e(Pref.class.toString(), e.toString());
		}
		return encoded;
	}
	public static void setPassword(String password){
		pwd = encodePassword(password);
		reencode();
	}
	public static String getPwd(){
		return pwd;
	}
	public static String hexString(byte[] b){
		if (b==null) return "";
		
		StringBuilder sb = new StringBuilder(b.length * 2);
		for (int i = 0; i < b.length; i++){
		int v = b[i] & 0xff;
		if (v < 16) {
			sb.append('0');
		}
		sb.append(Integer.toHexString(v));
		}
		return sb.toString();
	}
		
	public static String genEncAuth(String user, String passw){
		//Genera un string de autenticacion codificado
		//el parametro passw tiene que ser el password ENCRIPTADO con encodePassword
		//para mayor seguridad el password se evita pasar en plano, y siempre encodeado en lo posible
		//no es que sea super importante ya que el password se almacena encriptado, y ademas si algo puede acceder a la memoria del movil 
		//puedes ir olvidandote de cualquier seguridad, pero es una buena costumbre hacerlo
		String tmpEnc = "";
		try{
			//sha es una encripción rápida (un hash), una verdadera encripcion sería AES o BlowFish,
			//pero las implementaciones en android son demasiado complicadas y no vale la pena
			String userpassword = user + ":" + passw;
			tmpEnc =  "Basic " + Base64.encodeBytes(userpassword.getBytes("UTF-8")).toString();
		}
		catch (Exception  e){
			Log.e(Pref.class.toString(), e.toString());
		}
		return tmpEnc;
	}
}