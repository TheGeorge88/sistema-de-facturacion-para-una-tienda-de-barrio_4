<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Factura extends Model
{
    protected $table    = 'facturas';
    public    $timestamps = false;
    protected $fillable = [
        'numero','fecha','cliente_id','usuario_id',
        'subtotal','iva','descuento','total',
        'forma_pago','tipo_comprobante','estado','observaciones',
    ];
    protected $casts = ['fecha' => 'datetime'];

    public function cliente()
    {
        return $this->belongsTo(Cliente::class);
    }

    public function usuario()
    {
        return $this->belongsTo(Usuario::class, 'usuario_id');
    }

    public function detalles()
    {
        return $this->hasMany(DetalleFactura::class);
    }

    public static function siguienteNumero(): string
    {
        $max = static::max('id') ?? 0;
        return '001-001-' . str_pad($max + 1, 9, '0', STR_PAD_LEFT);
    }
}
