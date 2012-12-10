package com.moongate.bantatc;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.widget.EditText;

/**
 * @author MoonGate
 */
public class Configuracion extends Activity {
	private EditText esrv, euser, epwd;
	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.configuracion);
		esrv = (EditText) findViewById(R.id.c_ed_server);
		euser = (EditText) findViewById(R.id.c_ed_user);
		epwd = (EditText) findViewById(R.id.c_ed_pwd);
		
		//ponemos la ip visible
		esrv.setText(Pref.ip);
		euser.setText(Pref.user);
		//el password se guarda encriptado
		//epwd.setText(Pref.getPwd());
		//lo vaciamos para que no se vea el passwrd anterior.. 
		epwd.setText("");
		//basicamente evitamos que si alguien abre la app
	}
	public void guardar(View v){
		Pref.ip = esrv.getText().toString();
		Pref.user = euser.getText().toString();
		//no es bueno toquetear los passwords.. pero.. 
		//en android los teclados SUELEN incluir un espacio al final casi siempre
		String p = epwd.getText().toString().trim();
		if (p.length()> 0){
			//si puso algun password lo cambiamos.
			Pref.setPassword(p);
		}
		Pref.guardar(this);
		this.finish();
	}
}
