<?php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Usuario extends Model
{
    protected $table    = 'usuarios';
    public    $timestamps = false;
    protected $fillable = ['nombre','usuario','password','rol','activo'];
    protected $hidden   = ['password'];

    public function facturas()
    {
        return $this->hasMany(Factura::class, 'usuario_id');
    }
}
