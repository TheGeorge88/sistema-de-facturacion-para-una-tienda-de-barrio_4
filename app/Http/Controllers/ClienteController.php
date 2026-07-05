<?php
namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Cliente;

class ClienteController extends Controller
{
    public function index()
    {
        $clientes = Cliente::where('activo', 1)->orderBy('nombre')->get();
        return view('clientes.index', compact('clientes'));
    }

    public function create()
    {
        return view('clientes.form');
    }

    public function store(Request $request)
    {
        $data = $request->validate([
            'cedula'   => 'required|string|unique:clientes,cedula',
            'nombre'   => 'required|string|max:100',
            'apellido' => 'nullable|string|max:100',
            'direccion'=> 'nullable|string',
            'telefono' => 'nullable|string|max:20',
            'email'    => 'nullable|email|max:100',
            'tipo'     => 'required|in:natural,juridico',
        ]);
        $data['activo'] = 1;
        $cliente = Cliente::create($data);
        if ($request->expectsJson()) {
            return response()->json(['ok' => true, 'cliente' => [
                'id'       => $cliente->id,
                'cedula'   => $cliente->cedula,
                'nombre'   => trim("{$cliente->nombre} {$cliente->apellido}"),
                'telefono' => $cliente->telefono,
            ]]);
        }
        return redirect()->route('clientes.index')->with('success', 'Cliente registrado correctamente.');
    }

    public function edit(string $id)
    {
        $cliente = Cliente::findOrFail($id);
        return view('clientes.form', compact('cliente'));
    }

    public function update(Request $request, string $id)
    {
        $cliente = Cliente::findOrFail($id);
        $data = $request->validate([
            'cedula'   => "required|string|unique:clientes,cedula,$id",
            'nombre'   => 'required|string|max:100',
            'apellido' => 'nullable|string|max:100',
            'direccion'=> 'nullable|string',
            'telefono' => 'nullable|string|max:20',
            'email'    => 'nullable|email|max:100',
            'tipo'     => 'required|in:natural,juridico',
        ]);
        $cliente->update($data);
        return redirect()->route('clientes.index')->with('success', 'Cliente actualizado.');
    }

    public function destroy(string $id)
    {
        $c = Cliente::findOrFail($id);
        if ($c->cedula === '9999999999') {
            return back()->with('error', 'No puede eliminar al Consumidor Final.');
        }
        $c->update(['activo' => 0]);
        return redirect()->route('clientes.index')->with('success', 'Cliente eliminado.');
    }

    public function buscar(Request $request)
    {
        $q = $request->get('q', '');
        if (strlen($q) < 2) return response()->json([]);
        $clientes = Cliente::where('activo', 1)
            ->where(fn($w) => $w->where('cedula','like',"%$q%")
                                ->orWhere('nombre','like',"%$q%")
                                ->orWhere('apellido','like',"%$q%"))
            ->select('id','cedula','nombre','apellido','telefono')
            ->limit(10)->get()
            ->map(fn($c) => ['id'=>$c->id,'cedula'=>$c->cedula,
                             'nombre'=>trim("{$c->nombre} {$c->apellido}"),
                             'telefono'=>$c->telefono]);
        return response()->json($clientes);
    }

    public function show(string $id) { return redirect()->route('clientes.edit', $id); }
}
