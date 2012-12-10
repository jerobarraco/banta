package com.moongate.bantatc;
import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;

public class MainActivity extends Activity {
	public String ip, user, password;
	
	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_main);
		
		//obtenemos las preferencias guardadas
		//variable temporal con la ip default escrita en los resources
		Pref.cargar(this);
	}

  public void lanzar(Class c){
		//funcion que lanza una activity (pone el ip del textbox en las preferencias antes
		//Pref.ip = eIP.getText().toString() ;
		startActivity(new Intent(MainActivity.this, c));
	}
	public void man_pro(View v) {
		lanzar (mantenedor_pro.class);
	}
	public void graficos(View v) {
		lanzar(Graficos.class);
	}
	public void reportes(View v){
		lanzar(Reportes.class);
	}
	public void configuracion(View v){
		lanzar(Configuracion.class);
	}
	@Override
	protected void onStop(){
		//Al termianr las guardamos
		//esto no es muy necesario porque la config se guarda con el boton guardar en el activity configuracion
		super.onStop();
		Pref.guardar(this);
	}
}
