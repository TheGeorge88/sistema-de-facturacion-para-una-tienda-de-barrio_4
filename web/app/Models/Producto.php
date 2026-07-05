<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Producto extends Model
{
    protected $table    = 'productos';
    public    $timestamps = false;
    protected $fillable = [
        'codigo','descripcion','categoria_id','precio_compra',
        'precio_venta','precio_mayorista','stock','stock_minimo',
        'tiene_iva','activo',
    ];
    protected $casts = ['tiene_iva' => 'boolean', 'activo' => 'boolean'];

    public function categoria()
    {
        return $this->belongsTo(Categoria::class);
    }

    public function scopeActivos($query)
    {
        return $query->where('activo', 1);
    }
}
