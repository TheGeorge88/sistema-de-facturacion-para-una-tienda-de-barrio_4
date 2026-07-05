<?php
namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Usuario;

class AuthController extends Controller
{
    public function showLogin()
    {
        if (session('usuario')) {
            return redirect()->route('facturacion.index');
        }
        return view('auth.login');
    }

    public function login(Request $request)
    {
        $request->validate([
            'usuario'  => 'required|string',
            'password' => 'required|string',
        ]);

        $hash = hash('sha256', $request->password);
        $user = Usuario::where('usuario', $request->usuario)
                       ->where('password', $hash)
                       ->where('activo', 1)
                       ->first();

        if (!$user) {
            return back()->with('error', 'Usuario o contraseña incorrectos.');
        }

        session(['usuario' => $user->toArray()]);
        return redirect()->route('facturacion.index');
    }

    public function logout()
    {
        session()->forget('usuario');
        return redirect()->route('login');
    }
}
