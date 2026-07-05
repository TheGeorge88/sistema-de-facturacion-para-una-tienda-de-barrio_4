<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Cliente extends Model
{
    protected $table    = 'clientes';
    public    $timestamps = false;
    protected $fillable = [
        'cedula','nombre','apellido','direccion',
        'telefono','email','tipo','activo',
    ];

    public function facturas()
    {
        return $this->hasMany(Factura::class);
    }

    public function getNombreCompletoAttribute(): string
    {
        return trim("{$this->nombre} {$this->apellido}");
    }
}
