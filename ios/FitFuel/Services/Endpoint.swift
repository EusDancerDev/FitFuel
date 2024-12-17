import Foundation

enum HTTPMethod: String {
    case get = "GET"
    case post = "POST"
    case put = "PUT"
    case delete = "DELETE"
}

protocol Endpoint {
    var path: String { get }
    var method: HTTPMethod { get }
    var headers: [String: String] { get }
    var body: Encodable? { get }
}

enum APIEndpoint: Endpoint {
    case login(LoginRequest)
    case register(RegisterRequest)
    case menu
    case generateMenu(MenuPreferences)
    case statistics
    case syncWatchData(WatchData)
    
    var path: String {
        switch self {
        case .login: return "/auth/login"
        case .register: return "/auth/register"
        case .menu: return "/menu"
        case .generateMenu: return "/menu/generate"
        case .statistics: return "/statistics"
        case .syncWatchData: return "/watch-data/sync"
        }
    }
    
    var method: HTTPMethod {
        switch self {
        case .login, .register, .generateMenu, .syncWatchData:
            return .post
        case .menu, .statistics:
            return .get
        }
    }
    
    var headers: [String: String] {
        var headers = ["Content-Type": "application/json"]
        if let token = UserDefaults.standard.string(forKey: "authToken") {
            headers["Authorization"] = "Bearer \(token)"
        }
        return headers
    }
    
    var body: Encodable? {
        switch self {
        case .login(let request): return request
        case .register(let request): return request
        case .generateMenu(let preferences): return preferences
        case .syncWatchData(let data): return data
        default: return nil
        }
    }
} 