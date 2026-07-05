<?php
namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Usuario;

class UsuarioController extends Controller
{
    public function index()
    {
        $usuarios = Usuario::orderBy('nombre')->get();
        return view('usuarios.index', compact('usuarios'));
    }

    public function create()
    {
        return view('usuarios.form');
    }

    public function store(Request $request)
    {
        $data = $request->validate([
            'nombre'   => 'required|string|max:100',
            'usuario'  => 'required|string|unique:usuarios,usuario',
            'password' => 'required|string|min:4',
            'rol'      => 'required|in:admin,cajero',
        ]);
        $data['password'] = hash('sha256', $data['password']);
        $data['activo']   = 1;
        Usuario::create($data);
        return redirect()->route('usuarios.index')->with('success', 'Usuario creado correctamente.');
    }

    public function edit(string $id)
    {
        $usuario = Usuario::findOrFail($id);
        return view('usuarios.form', compact('usuario'));
    }

    public function update(Request $request, string $id)
    {
        $usuario = Usuario::findOrFail($id);
        $data = $request->validate([
            'nombre'  => 'required|string|max:100',
            'usuario' => "required|string|unique:usuarios,usuario,$id",
            'rol'     => 'required|in:admin,cajero',
            'activo'  => 'nullable',
        ]);
        $data['activo'] = $request->has('activo') ? 1 : 0;

        if ($request->filled('password')) {
            $request->validate(['password' => 'string|min:4']);
            $data['password'] = hash('sha256', $request->password);
        }
        $usuario->update($data);
        return redirect()->route('usuarios.index')->with('success', 'Usuario actualizado.');
    }

    public function destroy(string $id)
    {
        Usuario::findOrFail($id)->update(['activo' => 0]);
        return redirect()->route('usuarios.index')->with('success', 'Usuario desactivado.');
    }

    public function show(string $id) { return redirect()->route('usuarios.edit', $id); }
}
