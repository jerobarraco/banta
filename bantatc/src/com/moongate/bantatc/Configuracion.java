package com.moongate.bantatc;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;

/**
 * @author MoonGate
 */
public class Configuracion extends Activity {
	private EditText esrv, euser, epwd, eport;
	public String c_esrv, c_euser, c_epwd, c_eport;
	
	
	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.configuracion);
		esrv = (EditText) findViewById(R.id.c_ed_server);
		eport =  (EditText) findViewById(R.id.c_ed_port);
		euser = (EditText) findViewById(R.id.c_ed_user);
		epwd = (EditText) findViewById(R.id.c_ed_pwd);
		
		
		//ponemos la ip visible
		esrv.setText(Pref.ip);
		eport.setText(Pref.port);
		euser.setText(Pref.user);
		//epwd.setText(Pref.pwd);
		//el password se guarda encriptado
		//epwd.setText(Pref.getPwd());
		//lo vaciamos para que no se vea el passwrd anterior.. 
		//epwd.setText("");
		//basicamente evitamos que si alguien abre la app
	}

	public void limpiar(View v){
    esrv.setText("");
	eport.setText("");
	euser.setText("");
	epwd.setText("");
	}
	
	public void probar(View v){

		c_esrv = esrv.getText().toString();
		c_eport = eport.getText().toString();

		new wsTestCon().execute(this);

		}
	public void probar_u(View v){
		
		c_esrv = esrv.getText().toString();
		c_eport = eport.getText().toString();
		c_euser = euser.getText().toString();
		c_epwd = epwd.getText().toString();
		
		new wsTestUser().execute(this);
		
	}
	
	public void guardar(View v){
		Pref.ip = esrv.getText().toString();
		Pref.port = eport.getText().toString();
		String old_user = Pref.user;
		Pref.user = euser.getText().toString();
		//no es bueno toquetear los passwords.. pero.. 
		//en android los teclados SUELEN incluir un espacio al final casi siempre
		String p = epwd.getText().toString().trim();
		if (p.length()> 0){
			//si puso algun password lo cambiamos. se reencodea solo
			Pref.setPassword(p);
		}else{
			//si no se cambio, checkeamos si cambio le user.
			if (! Pref.user.equals(old_user)){
				Pref.reencode();
			}
		}
		Pref.guardar(this);
		this.finish();
	}
}
