<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;

class EgresoInventario extends Model
{
    protected $table      = 'egresos_inventario';
    public    $timestamps = false;
    protected $fillable   = ['fecha','producto_id','cantidad','motivo','observacion','usuario_id'];

    public function producto() { return $this->belongsTo(Producto::class); }
    public function usuario()  { return $this->belongsTo(Usuario::class); }
}
