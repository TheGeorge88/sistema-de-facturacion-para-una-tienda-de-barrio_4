<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class DetalleFactura extends Model
{
    protected $table    = 'detalle_facturas';
    public    $timestamps = false;
    protected $fillable = [
        'factura_id','producto_id','descripcion',
        'cantidad','precio_unitario','tiene_iva','subtotal',
    ];
    protected $casts = ['tiene_iva' => 'boolean'];

    public function producto()
    {
        return $this->belongsTo(Producto::class);
    }
}
