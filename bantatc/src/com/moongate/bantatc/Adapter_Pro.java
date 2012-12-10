package com.moongate.bantatc;
import com.moongate.bantatc.R;
import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import java.util.ArrayList;

import android.widget.ArrayAdapter;
import android.widget.TextView;

public class Adapter_Pro extends ArrayAdapter<Product> {
	private Context mycontext ;
	public Adapter_Pro(
					Context context, int textViewResourceId) {
		super(context, textViewResourceId, new ArrayList<Product>());
		this.mycontext = context;
	}
	public void addAll(Iterable<Product> ps){
		for (Product p:ps){
			this.add(p);
		}
		this.notifyDataSetChanged();
	}
	
	//Clase interna para cachear las instancias del view
	private class ViewHolder {
		TextView name;
		TextView code;
		TextView price;
		TextView stock;
	}
		 
	@Override
	public View getView(int position, View convertView, ViewGroup parent) {
		ViewHolder holder = null;
		if (convertView == null) {

			LayoutInflater vi = (LayoutInflater) mycontext.getSystemService(
				Context.LAYOUT_INFLATER_SERVICE);
			convertView = vi.inflate(R.layout.productview, null);
		 
			//creamos una instancia holder que mantenga referencias a los objetos del view
			//para accederlos despues
			holder = new ViewHolder();
			holder.code = (TextView) convertView.findViewById(R.id.Lv_pv_code1);
			holder.name = (TextView) convertView.findViewById(R.id.Lv_pv_name1);
			holder.price = (TextView) convertView.findViewById(R.id.Lv_pv_price1);
			holder.stock = (TextView) convertView.findViewById(R.id.Lv_pv_stock1);

			convertView.setTag(holder);
		 
		} else {
			holder = (ViewHolder) convertView.getTag();
		}
		 
		//toma el item desde la lista de producto almacenada internamente en el adapter
		Product product = this.getItem(position);
		holder.code.setText(product.code);
		holder.name.setText(product.name);
		holder.price.setText(product.price.toString());
		holder.stock.setText(product.stock.toString());

		return convertView;

	}
}
