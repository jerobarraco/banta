/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package com.moongate.bantatc;

public class Product {
	String name = "";
	String code = "";
	Double price = 0.0;
	Double stock = 0.0;
	@Override
	public String toString(){
		return String.format("[%s] (%s) $%s %s", code, stock, price, name);
	}
	public void fromJSon(String json){
		
	}
}
