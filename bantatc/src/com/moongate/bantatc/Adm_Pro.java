package com.moongate.bantatc;
import com.moongate.bantatc.R;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.TextView;

public class Adm_Pro extends Activity {
	public String search_code;
	public String old_code;
	public String code;
	public String name;
	public Double stock;
	public Double price;
	public String ip;
	
	TextView cdt_code;
	TextView cdt_name;
	TextView cdt_price;
	TextView cdt_stock;
/**
  * Called when the activity is first created.
  */
 @Override
 public void onCreate(Bundle icicle) {
  super.onCreate(icicle);
  setContentView(R.layout.adm_pro);
	Bundle extras = getIntent().getExtras();
	
	if(extras ==null) {
		search_code = "";
		old_code = "";
		code = "";
		name = "";
		price = 0d;
		stock = 0d;
		ip = "192.168.1.99";
	}
	else{
		search_code = extras.getString("search_code");
	/*	old_code = extras.getString("code");
		code = old_code;
		name = extras.getString("name");
		price = extras.getDouble("price");
		stock = extras.getDouble("stock");*/
		ip = extras.getString("ip");
	}
	
	cdt_code = (TextView) this.findViewById(com.moongate.bantatc.R.id.Txt_codigo);
	cdt_name = (TextView) this.findViewById(com.moongate.bantatc.R.id.txt_nombre);
	cdt_price = (TextView) this.findViewById(com.moongate.bantatc.R.id.txt_precio);
	cdt_stock = (TextView) this.findViewById(com.moongate.bantatc.R.id.txt_stock);
	
	this.cargar();
 }

  public void modificar(View v) {
		//aca llamar al webservice
		old_code = code ; //esto es por si el user cambio el codigo
		code = cdt_code.getText().toString();
		name = cdt_name.getText().toString();
		//y lo mismo con las otras variables
		stock = Double.valueOf(cdt_stock.getText().toString());
		price = Double.valueOf(cdt_price.getText().toString());
	  new wsModProducts().execute(this);
	}
	public void eliminar(View v){
		new wsDelProducts().execute(this);
		
	}
	public void cargar(){
		new wsDetailProduct().execute(this);
	}
	public void llenar(Product p){
		//esto permite 2 cosas
		//primero, si el producto no se encuentra, rellena los campos de codigo para 
		//que al poner modificar, se ingrese uno nuevo
		//tambien permite que se modifique si ya existe
		this.old_code = p.code;
		this.code = p.code;
		cdt_code.setText(p.code); 
		cdt_name.setText(p.name); 
		cdt_price.setText(Double.toString(p.price)); 
		cdt_stock.setText(Double.toString(p.stock)); 
	}
	public void terminar(){
		this.finish();
	}
 }
