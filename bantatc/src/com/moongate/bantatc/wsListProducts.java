package com.moongate.bantatc;

import android.app.ProgressDialog;
import android.net.Uri;
import android.os.AsyncTask;
import android.util.Log;
import android.widget.Toast;
import java.util.ArrayList;
import org.apache.http.client.methods.HttpGet;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

public class wsListProducts extends AsyncTask<mantenedor_pro, Void, ArrayList<Product>> {
	private ProgressDialog dialog;
	public ArrayList<Product> products;	 
	private mantenedor_pro padre;
	private wsBase ws = new wsBase();
	@Override
	protected ArrayList<Product> doInBackground(mantenedor_pro... class_padre) {
		this.padre = class_padre[0];
		this.padre.cargando = true; //no muy thread-safe pero necesario
		
		Uri.Builder b = Uri.parse("http://"+Pref.ip+":8080").buildUpon();
		b.path("/prods");
		//que pida los datos comenzando desde la pagina a cargar
		String start = String.valueOf(this.padre.cargar * this.padre.pagina);
		
		String limit = String.valueOf(this.padre.cargar );
		b.appendQueryParameter("start", start);
		b.appendQueryParameter("limit", limit);
		b.appendQueryParameter("search_name", this.padre.search_name);
		b.appendQueryParameter("order_by", this.padre.order_by);
		b.appendQueryParameter("order_asc", this.padre.order_asc);
		String url = b.build().toString();

		HttpGet httpGet = new HttpGet(url);
		return decodeJSON(this.ws.doRequest(httpGet));
	}
	private ArrayList<Product> decodeJSON(JSONObject r){
		//creamos un array vacio en caso que haya error lo devolvemos igual
		products = new ArrayList<Product>();
		//Si no hubo error en el ws
		if (this.ws.success){
			try {
				//obtenemos el array de productos
				JSONArray prodList = r.getJSONArray("data");
				//lo iteramos
				for (int i=0; i<prodList.length(); i++){
					JSONObject prod_info = prodList.getJSONObject(i);
					//creamos un nuevo objeto por cada item
					Product prod = new Product();
					prod.name = prod_info.getString("name");
					prod.code = prod_info.getString("code");
					prod.price = prod_info.getDouble("price");
					prod.stock = prod_info.getDouble("stock");

					//y lo agregamos
					products.add(prod);
				}
			} catch (JSONException ex) {
				this.ws.success = false;
				this.ws.error = ex.toString();
				Log.e(wsListProducts.class.getName(), this.ws.error);
			}
		}
		return products;
	}	
		   
	@Override
	public void onPostExecute(ArrayList<Product> products){
		String msg;
		if (this.ws.success){
			if (this.padre.pagina == 0){
				//pagina == 0 indica un reset
				//eliminamos los productos del adaptador 
				//(esto es mas eficiente que recrear el adaptador)
				this.padre.adapter.clear();
				//y le decimos a la lista q se vaya al principio para evitar que cargue 2 veces seguidas
				this.padre.lv.scrollTo(0, 0);
			}
			//si no hay productos, como que llegamos al "final" 
			if (products.size() == 0 ){
				this.padre.end = true;
			}else{
				//sino , agregamos todos
				//notar que modificamos el adaptador para poder hacer addAll
				this.padre.adapter.addAll(products);
			}
			this.padre.total = this.padre.adapter.getCount();
			msg = "Cargados " + String.valueOf(this.padre.total) + " productos";
			if (this.padre.end){
				msg += ". Fin de la lista";
			}
		}else{
			//Mostramos un popup con el error
			Toast.makeText( this.padre, "Error. "+ws.error, Toast.LENGTH_LONG).show();
			//necesario para que no siga cargando como wn
			this.padre.end = true;
			//y ponemos un mensaje de error en el label
			msg = "Error al cargar." ;
		}
	
		this.padre.cdHttp.setText(msg);
		this.padre.cargando = false;			
	}
}
		
