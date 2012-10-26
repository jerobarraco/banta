/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package com.moongate.bantatc;

/**
 *
 * @author Administrador
 */
public class Product {
	String name;
	String code;
	Double price;
	Double stock;
	@Override
	public String toString(){
		return String.format("[%s] (%s) $%s %s", code, stock, price, name);
	}
}
