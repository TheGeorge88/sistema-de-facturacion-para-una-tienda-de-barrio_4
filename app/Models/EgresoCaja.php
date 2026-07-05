<?php
namespace App\Models;
use Illuminate\Database\Eloquent\Model;

class EgresoCaja extends Model
{
    protected $table      = 'egresos_caja';
    public    $timestamps = false;
    protected $fillable   = ['fecha','concepto','monto','metodo_pago','observacion','usuario_id'];

    public function usuario() { return $this->belongsTo(Usuario::class); }
}
